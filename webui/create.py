
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW
from toga_web.libs import create_element

from .util import clipboard_copy


class ImportWallet(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "import_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.app = app

        self.is_seed_trigger = False

        back_button_icon = create_element(
            "sl-icon",
            id="import_back_button_icon",
            name="arrow-return-left"
        )

        back_button_label = toga.Label(
            id="import_back_button_label",
            text="Cancel"
        )

        self.back_button = toga.Box(
            id="import_back_button",
            style=Pack(
                direction=ROW
            )
        )

        seed_tab_label = toga.Label(
            id="import_seed_tab_label",
            text="Seed Phrase"
        )
        self.seed_tab = toga.Box(
            id="import_seed_tab",
            style=Pack(
                direction=ROW
            )
        )

        wif_tab_label = toga.Label(
            id="import_wif_tab_label",
            text="WIF"
        )
        self.wif_tab = toga.Box(
            id="import_wif_tab",
            style=Pack(
                direction=ROW
            )
        )

        switch_box = toga.Box(
            id="import_switch_box",
            style=Pack(
                direction=ROW
            )
        )

        self.key_input = toga.PasswordInput(
            style=Pack(
                flex=1
            )
        )
        self.key_input._impl.native.autocomplete="off"
        self.key_input._impl.native.passwordToggle = True

        key_box = toga.Box(
            id="import_key_box"
        )

        save_icon = create_element(
            "sl-icon",
            id="import_save_icon",
            name="floppy"
        )
        save_label = toga.Label(
            id="import_save_label",
            text="Save"
        )

        self.save_button = toga.Box(
            id="import_save_button",
            style=Pack(
                direction=ROW
            )
        )

        buttons_box = toga.Box(
            id="import_buttons_box",
            style=Pack(
                direction=ROW
            )
        )

        self.add(
            self.back_button,
            switch_box,
            key_box,
            buttons_box
        )
        self.back_button._impl.native.appendChild(
            back_button_icon
        )
        self.back_button.add(
            back_button_label
        )
        switch_box.add(
            self.seed_tab,
            self.wif_tab
        )
        self.seed_tab.add(
            seed_tab_label
        )
        self.wif_tab.add(
            wif_tab_label
        )
        key_box.add(
            self.key_input
        )
        buttons_box.add(
            self.save_button
        )
        self.save_button._impl.native.appendChild(
            save_icon
        )
        self.save_button.add(
            save_label
        )

        self.set_default_tab()


    def set_default_tab(self):
        self.set_seed_tab()

    def set_seed_tab(self):
        self.is_seed_trigger = True
        self.key_input.value = ""
        self.key_input.placeholder = "Enter seed phrase (12 words)"
        self.wif_tab._impl.native.classList.remove("active")
        self.seed_tab._impl.native.classList.add("active")

    def set_wif_tab(self):
        self.is_seed_trigger = False
        self.key_input.value = ""
        self.key_input.placeholder = "Enter WIF key"
        self.seed_tab._impl.native.classList.remove("active")
        self.wif_tab._impl.native.classList.add("active")



class NewWallet(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "new_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.app = app

        back_button_icon = create_element(
            "sl-icon",
            id="new_back_button_icon",
            name="arrow-return-left"
        )

        back_button_label = toga.Label(
            id="new_back_button_label",
            text="Cancel"
        )

        self.back_button = toga.Box(
            id="new_back_button",
            style=Pack(
                direction=ROW
            )
        )

        note_label = toga.Label(
            id="new_note_label",
            text="Your seed phrase grants full access to your wallet, keep it safe and offline never share it with anyone, if it is lost or compromised your funds cannot be recovered, and you are solely responsible for its protection"
        )

        note_box = toga.Box(
            id="new_note_box"
        )

        seed_label = toga.Label(
            id="new_seed_label",
            text="Seed Phrase (12 words)"
        )

        self.seed_value = toga.Label(
            id="new_seed_value",
            text=""
        )
        seed_value_box = toga.Box(
            id="new_seed_value_box"
        )

        copy_icon = create_element(
            "sl-icon",
            id="new_copy_icon",
            name="clipboard2"
        )
        copy_label = toga.Label(
            id="new_copy_label",
            text="Copy"
        )

        self.copy_button = toga.Box(
            id="new_copy_button",
            style=Pack(
                direction=ROW
            )
        )
        self.copy_button._impl.native.onclick = self.on_copy_click

        save_icon = create_element(
            "sl-icon",
            id="new_save_icon",
            name="floppy"
        )
        save_label = toga.Label(
            id="new_save_label",
            text="Save"
        )

        self.save_button = toga.Box(
            id="new_save_button",
            style=Pack(
                direction=ROW
            )
        )

        buttons_box = toga.Box(
            id="new_buttons_box",
            style=Pack(
                direction=ROW
            )
        )

        self.add(
            self.back_button,
            note_box,
            seed_label,
            seed_value_box,
            buttons_box
        )
        self.back_button._impl.native.appendChild(
            back_button_icon
        )
        self.back_button.add(
            back_button_label
        )
        note_box.add(
            note_label
        )
        seed_value_box.add(
            self.seed_value
        )
        buttons_box.add(
            self.copy_button,
            self.save_button
        )
        self.copy_button._impl.native.appendChild(
            copy_icon
        )
        self.copy_button.add(
            copy_label
        )
        self.save_button._impl.native.appendChild(
            save_icon
        )
        self.save_button.add(
            save_label
        )


    def make_seed(self):
        from btczpy.mnemonic import Mnemonic
        seed = Mnemonic('en').make_seed()
        self.seed_value.text = seed


    def on_copy_click(self, event):
        value = self.seed_value.text
        clipboard_copy(value)


class Create(toga.Box):
    def __init__(self):
        super().__init__(
            id= "create_box",
            style=Pack(
                direction=COLUMN
            )
        )

        back_button_icon = create_element(
            "sl-icon",
            id="create_back_button_icon",
            name="arrow-return-left"
        )

        back_button_label = toga.Label(
            id="create_back_button_label",
            text="Return"
        )

        self.back_button = toga.Box(
            id="create_back_button",
            style=Pack(
                direction=ROW
            )
        )

        new_button_icon = create_element(
            "sl-icon",
            id="create_new_button_icon",
            name="plus-circle"
        )

        new_button_label = toga.Label(
            id="create_new_button_label",
            text="New Wallet"
        )

        self.new_button = toga.Box(
            id="create_new_button",
            style=Pack(
                direction=ROW
            )
        )

        import_button_icon = create_element(
            "sl-icon",
            id="create_import_button_icon",
            name="arrow-bar-down"
        )

        import_button_label = toga.Label(
            id="create_import_button_label",
            text="Import Wallet"
        )

        self.import_button = toga.Box(
            id="create_import_button",
            style=Pack(
                direction=ROW
            )
        )

        self.add(
            self.back_button,
            self.new_button,
            self.import_button
        )
        self.back_button._impl.native.appendChild(
            back_button_icon
        )
        self.back_button.add(
            back_button_label
        )
        self.new_button._impl.native.appendChild(
            new_button_icon
        )
        self.new_button.add(
            new_button_label
        )
        self.import_button._impl.native.appendChild(
            import_button_icon
        )
        self.import_button.add(
            import_button_label
        )