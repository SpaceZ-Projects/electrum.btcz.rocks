
import asyncio
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW
from toga_web.libs import create_element

from .wallet import Wallet, list_accounts, create_account, get_account, decrypt_key
from .create import Create, NewWallet, ImportWallet
from .widget import Tooltip, Alert
from .dialog import Password
from .util import is_strong_password


class Account(toga.Box):
    def __init__(self, account):
        super().__init__(
            id= "account_widget",
            style=Pack(
                direction=ROW
            )
        )

        name = account["name"]

        account_icon = create_element(
            "sl-icon",
            id="account_widget_icon",
            name="wallet"
        )

        account_name_label = toga.Label(
            id="account_name_label",
            text=name
        )

        self.add(
            account_name_label
        )
        self._impl.native.appendChild(
            account_icon
        )


class Accounts(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "accounts_page",
            style=Pack(
                direction=COLUMN,
                flex=1
            )
        )

        self.app = app
        self.active_panel = None
        self.password_dialog = None

        self.accounts_ids = []
        self.account_id = None

        self.create_panel = Create()
        self.new_panel = NewWallet(self.app)
        self.import_panel = ImportWallet(self.app)

        self.create_panel.new_button._impl.native.onclick = self.on_new_click
        self.create_panel.import_button._impl.native.onclick = self.on_import_click

        self.create_panel.back_button._impl.native.onclick = self.on_cancel_create
        self.new_panel.back_button._impl.native.onclick = self.on_cancel_create
        self.import_panel.back_button._impl.native.onclick = self.on_cancel_create

        self.new_panel.save_button._impl.native.onclick = self.on_save_new_click
        self.import_panel.seed_tab._impl.native.onclick = self.on_seed_tab_click
        self.import_panel.wif_tab._impl.native.onclick = self.on_wif_tab_click
        self.import_panel.save_button._impl.native.onclick = self.on_save_imported_click

        electrum_title = create_element(
            "img",
            id="accounts_electrum_title",
            src="/static/assets/Title.png"
        )

        self.status_icon = create_element(
            "sl-icon",
            classes=["status_icon"],
            name="circle-fill"
        )
        self.status_icon.classList.add("retry")
        
        self.status_tooltip = Tooltip(text="", duration=3000)
        self.status_tooltip.attach_to(self.status_icon)

        electrum_height_icon = create_element(
            "sl-icon",
            classes=["electrum_height_icon"],
            name="boxes"
        )

        self.electrum_height_value = toga.Label(
            text="Connecting..."
        )
        self.electrum_height_value._impl.native.className = "electrum_height_value"

        self.electrum_version_value = toga.Label(
            text="V : "
        )
        self.electrum_version_value._impl.native.className = "electrum_version_value"

        self.electrum_protocol_value = toga.Label(
            text="Proto : "
        )
        self.electrum_protocol_value._impl.native.className = "electrum_protocol_value"

        electrum_status_box = toga.Box(
            id="electrum_status_box",
            style=Pack(
                direction=ROW
            )
        )

        electrum_info_box = toga.Box(
            id="electrum_info_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.notfound_label = toga.Label(
            id="accounts_notfound_label",
            text="No accounts are available"
        )

        self.accounts_list_box = toga.Box(
            id="accounts_list_box",
            style=Pack(
                direction=COLUMN
            )
        )

        add_account_icon = create_element(
            "sl-icon",
            "accounts_add_account_icon",
            name="person-add"
        )

        add_account_label = toga.Label(
            id="accounts_add_account_label",
            text="Create Account"
        )

        self.add_account_button = toga.Box(
            id="accounts_add_account_button",
            style=Pack(
                direction=ROW
            )
        )
        self.add_account_button._impl.native.onclick = self.on_add_account_click

        self.accounts_box = toga.Box(
            id="accounts_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self._impl.native.appendChild(
            electrum_title
        )
        self.add(
            electrum_info_box,
            self.accounts_box,
            self.create_panel,
            self.new_panel,
            self.import_panel
        )
        electrum_info_box.add(
            electrum_status_box
        )
        electrum_status_box._impl.native.appendChild(
            self.status_icon
        )
        electrum_status_box._impl.native.appendChild(
            electrum_height_icon
        )
        electrum_status_box.add(
            self.electrum_height_value,
            self.electrum_version_value,
            self.electrum_protocol_value
        )
        self.accounts_box.add(
            self.accounts_list_box,
            self.add_account_button
        )
        self.add_account_button._impl.native.appendChild(
            add_account_icon
        )
        self.add_account_button.add(
            add_account_label
        )


    def verify_accounts(self):
        self.show_accounts_panel()
        self.load_accounts()

    def load_accounts(self):
        accounts = list_accounts()
        if not accounts:
            self.accounts_list_box.add(
                self.notfound_label
            )
            return
        for account in accounts:
            id = account["id"]
            name = account["name"]
            account_widget = Account(account)
            account_widget._impl.native.onclick = lambda event, id=id, name=name: self.on_account_click(id, name)
            self.accounts_list_box._impl.native.appendChild(
                account_widget._impl.native
            )
            self.accounts_ids.append(id)


    def reload_accounts(self):
        native = self.accounts_list_box._impl.native
        while native.firstChild:
            native.removeChild(native.firstChild)

        self.accounts_ids.clear()

        accounts = list_accounts()
        for account in accounts:
            id = account["id"]
            name = account["name"]
            account_widget = Account(account)
            account_widget._impl.native.onclick = lambda event, id=id, name=name: self.on_account_click(id, name)
            self.accounts_list_box._impl.native.appendChild(
                account_widget._impl.native
            )
            self.accounts_ids.append(id)
        

    async def panels_transition(self, active_panel):
        if self.active_panel:
            self.active_panel._impl.native.classList.remove("active")
            await asyncio.sleep(0.2)
            self.active_panel._impl.native.classList.remove("show")
        active_panel._impl.native.classList.add('show')
        await asyncio.sleep(0.2)
        active_panel._impl.native.classList.add('active')
        self.active_panel = active_panel


    def set_active(self, active_panel):
        self.app.loop.create_task(self.panels_transition(active_panel))

    def show_accounts_panel(self):
        self.set_active(self.accounts_box)


    def on_add_account_click(self, event):
        self.set_active(self.create_panel)


    def on_cancel_create(self, event):
        if self.password_dialog:
            self.password_dialog.hide()
            self.password_dialog = None
        self.show_accounts_panel()

    def on_cancel_login(self, event):
        if self.password_dialog:
            self.account_id = None
            self.password_dialog.hide()
            self.password_dialog = None

    def on_new_click(self, event):
        self.set_active(self.new_panel)
        self.new_panel.make_seed()

    def on_import_click(self, event):
        self.set_active(self.import_panel)

    def on_save_new_click(self, event):
        self.password_dialog = Password("create")
        self.password_dialog.cancel_button._impl.native.onclick = self.on_cancel_create
        self.password_dialog.confirm_button._impl.native.onclick = self.on_confirm_new
        self.password_dialog.show()

    def on_confirm_new(self, event):
        wallet_name = self.password_dialog.name_input.value.strip()
        password = self.password_dialog.password_input.value.strip()
        if not password:
            return
        if self.password_dialog.is_degit:
            if len(password) < 6:
                return
        else:
            error = is_strong_password(password)
            if error is not None:
                self.password_dialog.show_error(error)
                return
        seed = self.new_panel.seed_value.text
        if not wallet_name:
            wallet_name = None
        account = create_account(seed, password, wallet_name)
        if not account:
            self.password_dialog.show_error("Account name already exists")
            return
        self.password_dialog.hide()
        self.password_dialog = None
        self.show_accounts_panel()
        self.reload_accounts()

    def on_seed_tab_click(self, event):
        self.import_panel.set_seed_tab()

    def on_wif_tab_click(self, event):
        self.import_panel.set_wif_tab()

    def on_cancel_import(self, event):
        if self.password_dialog:
            self.password_dialog.hide()
            self.password_dialog = None
        self.import_panel.key_input.value = ""

    def on_save_imported_click(self, event):
        value = self.import_panel.key_input.value.strip()
        if not value:
            return
        if self.import_panel.is_seed_trigger:
            from btczpy.keystore import is_seed
            if not is_seed(value):
                Alert().show("Invalid seed phrase", "warning")
                return
        else:
            from btczpy.crypto import deserialize_privkey
            try:
                deserialize_privkey(value)
            except Exception:
                Alert().show("Invalid wif key", "warning")
                return
        self.password_dialog = Password("create")
        self.password_dialog.cancel_button._impl.native.onclick = self.on_cancel_import
        self.password_dialog.confirm_button._impl.native.onclick = self.on_confirm_import
        self.password_dialog.show()

    def on_confirm_import(self, event):
        wallet_name = self.password_dialog.name_input.value.strip()
        password = self.password_dialog.password_input.value.strip()
        if not password:
            return
        if self.password_dialog.is_degit:
            if len(password) < 6:
                return
        else:
            error = is_strong_password(password)
            if error is not None:
                self.password_dialog.show_error(error)
                return
        value = self.import_panel.key_input.value.strip()
        if not wallet_name:
            wallet_name = None
        if self.import_panel.is_seed_trigger:
            type = "standard"
        else:
            type = "wif"
        account = create_account(value, password, wallet_name, type, "imported")
        if not account:
            self.password_dialog.show_error("Account name already exists")
            return
        self.password_dialog.hide()
        self.password_dialog = None
        self.show_accounts_panel()
        self.reload_accounts()
        

    def on_account_click(self, id, name):
        self.account_id = id
        self.password_dialog = Password("login", name)
        self.password_dialog.cancel_button._impl.native.onclick = self.on_cancel_login
        self.password_dialog.confirm_button._impl.native.onclick = self.on_confirm_login
        self.password_dialog._on_confirm = self.on_confirm_login
        self.password_dialog.show()


    def on_confirm_login(self, event):
        password = self.password_dialog.password_input.value.strip()
        if not password:
            return
        timer = self.password_dialog.timer_slider.value
        self.password_dialog.error_box._impl.native.classList.remove("active")
        account = get_account(self.account_id)
        name = account["name"]
        enc_key = account["encrypt"]
        type = account["type"]
        status = account["status"]
        try:
            decrypted = decrypt_key(enc_key, password)
            if decrypted:
                self.app.wallet = Wallet()
                self.app.wallet.id = self.account_id
                self.app.wallet.name = name
                self.app.wallet.update(enc_key, type, status)
                self.app.wallet.get_address(password)
                if timer > 0:
                    self.app.wallet.cache_password(password, timer)
                self.app.main_window.show_wallet()
                self.password_dialog.hide()
                self.password_dialog = None
        except Exception:
            self.password_dialog.show_error("Invalid Password")


    def update_status(self, status):
        if status == "connected":
            self.status_icon.classList.remove("retry")
            self.status_icon.classList.remove("off")
            self.status_icon.classList.add("on")
        elif status == "disconnected":
            self.status_icon.classList.remove("retry")
            self.status_icon.classList.remove("on")
            self.status_icon.classList.add("off")
        elif status in ["reconnecting", "connecting"]:
            self.status_icon.classList.remove("off")
            self.status_icon.classList.remove("on")
            self.status_icon.classList.add("retry")

    def update_height(self, height):
        self.electrum_height_value.text = height

    def update_version(self, version, protocol):
        self.electrum_version_value.text = f"V : {version}"
        self.electrum_protocol_value.text = f"Proto : {protocol}"
        self.status_tooltip.text = self.app.client.url

