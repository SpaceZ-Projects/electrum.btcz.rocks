
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW
from toga_web.libs import create_element

from .dialog import Password, Logout, Delete
from .wallet import update_password, delete_account
from .util import is_strong_password, clipboard_copy
from .widget import Alert, Drawer



class BackUp(Drawer):
    def __init__(self, decrypted):
        super().__init__(
            title="Backup Wallet",
            placement="bottom",
            size="fit-content",
            border_radius="20px"
        )

        note_label = toga.Label(
            id="backup_note_label",
            text="Your seed phrase grants full access to your wallet, keep it safe and offline never share it with anyone, if it is lost or compromised your funds cannot be recovered, and you are solely responsible for its protection"
        )

        note_box = toga.Box(
            id="backup_note_box"
        )

        value = toga.Label(
            id="backup_value",
            text=decrypted
        )
        value_box = toga.Box(
            id="backup_value_box"
        )

        copy_icon = create_element(
            "sl-icon",
            id="backup_copy_icon",
            name="clipboard2"
        )
        copy_label = toga.Label(
            id="backup_copy_label",
            text="Copy"
        )

        self.copy_button = toga.Box(
            id="backup_copy_button",
            style=Pack(
                direction=ROW
            )
        )

        self.add(
            note_box._impl.native,
            value_box._impl.native,
            self.copy_button._impl.native
        )
        note_box.add(
            note_label
        )
        value_box.add(
            value
        )
        self.copy_button._impl.native.appendChild(
            copy_icon
        )
        self.copy_button.add(
            copy_label
        )


class Settings(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "settings_page",
            style=Pack(
                direction=COLUMN,
                flex=1
            )
        )

        self.app = app

        self.password_dialog = None
        self.backup_drawer = None
        self.delete_dialog = None
        self.logout_dialog = None

        password_button_icon = create_element(
            "sl-icon",
            id="settings_password_button_icon",
            name="person-lock"
        )

        password_button_label = toga.Label(
            id="settings_password_button_label",
            text="Update Password"
        )

        self.password_button = toga.Box(
            id="settings_password_button",
            style=Pack(
                direction=ROW
            )
        )
        self.password_button._impl.native.onclick = self.on_change_password_click

        backup_button_icon = create_element(
            "sl-icon",
            id="settings_backup_button_icon",
            name="database-gear"
        )

        backup_button_label = toga.Label(
            id="settings_backup_button_label",
            text="Backup Wallet"
        )

        self.backup_button = toga.Box(
            id="settings_backup_button",
            style=Pack(
                direction=ROW
            )
        )
        self.backup_button._impl.native.onclick = self.on_backup_click

        delete_button_icon = create_element(
            "sl-icon",
            id="settings_delete_button_icon",
            name="trash"
        )

        delete_button_label = toga.Label(
            id="settings_delete_button_label",
            text="Delete Wallet"
        )

        self.delete_button = toga.Box(
            id="settings_delete_button",
            style=Pack(
                direction=ROW
            )
        )
        self.delete_button._impl.native.onclick = self.on_delete_click

        manage_wallet_label = toga.Label(
            id="settings_manage_wallet_label",
            text="Manage Wallet :"
        )

        manage_buttons_box = toga.Box(
            id="settings_manage_buttons_box",
        )

        manage_wallet_box = toga.Box(
            id="settings_manage_wallet_box",
            style=Pack(
                direction=ROW
            )
        )

        logout_button_icon = create_element(
            "sl-icon",
            id="settings_logout_button_icon",
            name="door-open"
        )

        logout_button_label = toga.Label(
            id="settings_logout_button_label",
            text="Logout"
        )

        self.logout_button = toga.Box(
            id="settings_logout_button",
            style=Pack(
                direction=ROW
            )
        )
        self.logout_button._impl.native.onclick = self.on_logout_click

        logout_box = toga.Box(
            id="settings_logout_box",
            style=Pack(
                direction=ROW
            )
        )

        self.add(
            manage_wallet_box,
            logout_box
        )
        manage_wallet_box.add(
            manage_wallet_label,
            manage_buttons_box
        )
        manage_buttons_box.add(
            self.password_button,
            self.backup_button,
            self.delete_button
        )
        self.password_button._impl.native.appendChild(
            password_button_icon
        )
        self.password_button.add(
            password_button_label
        )
        self.backup_button._impl.native.appendChild(
            backup_button_icon
        )
        self.backup_button.add(
            backup_button_label
        )
        self.delete_button._impl.native.appendChild(
            delete_button_icon
        )
        self.delete_button.add(
            delete_button_label
        )

        logout_box.add(
            self.logout_button
        )
        self.logout_button._impl.native.appendChild(
            logout_button_icon
        )
        self.logout_button.add(
            logout_button_label
        )


    def on_change_password_click(self, event):
        self.password_dialog = Password("update")
        self.password_dialog.cancel_button._impl.native.onclick = self.on_cancel_password
        self.password_dialog.confirm_button._impl.native.onclick = self.on_confirm_change
        self.password_dialog.show()


    def on_cancel_password(self, event):
        if self.password_dialog:
            self.password_dialog.hide()
            self.password_dialog = None


    def on_confirm_change(self, event):
        old_password = self.password_dialog.old_password_input.value.strip()
        new_password = self.password_dialog.password_input.value.strip()
        if not old_password or not new_password:
            return
        if self.password_dialog.is_degit:
            if len(new_password) < 6:
                return
        else:
            error = is_strong_password(new_password)
            if error is not None:
                self.password_dialog.show_error(error)
                return
        result = update_password(self.app.wallet.id, old_password, new_password)
        if not result:
            self.password_dialog.show_error("Invalid old Password")
            return
        self.app.wallet.update(result, password=new_password)
        self.password_dialog.hide()
        self.password_dialog = None
        Alert().show("Password has been updated", variant="success")


    def on_backup_click(self, event):
        if self.app.wallet.is_unlocked():
            decrypted = self.decrypt_key()
            if decrypted:
                self.show_key(decrypted)
                return
        self.password_dialog = Password(name=self.app.wallet.name)
        self.password_dialog.cancel_button._impl.native.onclick = self.on_cancel_password
        self.password_dialog.confirm_button._impl.native.onclick = self.on_confirm_backup
        self.password_dialog.show()


    def on_confirm_backup(self, event):
        password = self.password_dialog.password_input.value.strip()
        if not password:
            return
        timer = self.password_dialog.timer_slider.value
        decrypted = self.decrypt_key(password)
        if not decrypted:
            self.password_dialog.show_error("Invalid Password")
            return
        self.show_key(decrypted)
        if timer > 0:
            self.app.wallet.cache_password(password, timer)
        self.password_dialog.hide()
        self.password_dialog = None
            

    def decrypt_key(self, password = None):
        try:
            return self.app.wallet.decrypt_key(password)
        except Exception:
            return None

    def show_key(self, key):
        self.backup_drawer = BackUp(key)
        self.backup_drawer.on_after_hide = self.on_backup_hide
        self.backup_drawer.copy_button._impl.native.onclick = lambda event, decrypted=key: self.on_copy_click(key)
        self.backup_drawer.show()


    def on_delete_click(self, event):
        self.delete_dialog = Delete(self.app.wallet.address)
        self.delete_dialog.cancel_button._impl.native.onclick = self.on_cancel_delete
        self.delete_dialog.confirm_button._impl.native.onclick = self.on_confirm_delete
        self.delete_dialog.show()


    def on_confirm_delete(self, event):
        text = self.delete_dialog.verify_input.value.strip()
        if not text:
            return
        address = self.app.wallet.address
        short_address = f"delete {address[:3]}...{address[-3:]}"
        if text != short_address:
            return
        delete_account(self.app.wallet.id)
        self.app.main_window.logout_account()
        self.delete_dialog.hide()
        self.delete_dialog = None


    def on_backup_hide(self, event):
        self.backup_drawer = None

    def on_copy_click(self, decrypted):
        clipboard_copy(decrypted)


    def on_cancel_delete(self, event):
        if self.delete_dialog:
            self.delete_dialog.hide()
            self.delete_dialog = None


    def on_logout_click(self, event):
        self.logout_dialog = Logout()
        self.logout_dialog.confirm_button._impl.native.onclick = self.on_confirm_logout
        self.logout_dialog.cancel_button._impl.native.onclick = self.on_cancel_logout
        self.logout_dialog.on_hide = self.on_cancel_logout
        self.logout_dialog.show()


    def on_confirm_logout(self, event):
        self.app.wallet.clear()
        self.app.main_window.logout_account()
        self.logout_dialog.hide()
        self.logout_dialog = None

    def on_cancel_logout(self, event):
        if self.logout_dialog:
            self.logout_dialog.hide()
            self.logout_dialog = None