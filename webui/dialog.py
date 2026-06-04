
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW
from toga_web.libs import create_element
from pyodide.ffi import create_proxy

from .widget import Dialog


class Delete(Dialog):
    def __init__(self, address):
        super().__init__(
            title="Delete Wallet",
            closable=False
        )

        self.short_address = f"delete {address[:3]}...{address[-3:]}"

        self.error_label = toga.Label(
            id="delete_error_label",
            text=""
        )

        self.error_box = toga.Box(
            id="delete_error_box",
            style=Pack(
                direction=ROW
            )
        )

        self.verify_input = toga.TextInput(
            placeholder=f'Type "{self.short_address}" to confirm',
            on_change=self.on_verify_change
        )
        self.verify_input._impl.native.autocomplete="off"

        cancel_label = toga.Label(
            id="delete_cancel_label",
            text="Cancel"
        )

        self.cancel_button = toga.Box(
            id="delete_cancel_button",
            style=Pack(
                direction=ROW
            )
        )

        confirm_label = toga.Label(
            id="delete_confirm_label",
            text="Delete"
        )

        self.confirm_button = toga.Box(
            id="delete_confirm_button",
            style=Pack(
                direction=ROW
            )
        )

        buttons_box = toga.Box(
            id="delete_buttons_box",
            style=Pack(
                direction=ROW
            )
        )

        dialog_box = toga.Box(
            id="delete_dialog",
            style=Pack(
                direction=COLUMN
            )
        )

        self.add(
            dialog_box._impl.native
        )

        dialog_box.add(
            self.error_box,
            self.verify_input,
            buttons_box
        )
        self.error_box.add(
            self.error_label
        )
        buttons_box.add(
            self.cancel_button,
            self.confirm_button
        )
        self.cancel_button.add(
            cancel_label
        )
        self.confirm_button.add(
            confirm_label
        )


    def on_verify_change(self, event):
        if not event.value:
            return
        if event.value.strip() != self.short_address:
            self.show_error(f'Type must exactly match "{self.short_address}"')
        elif event.value.strip() == self.short_address:
            self.hide_error()

    def hide_error(self):
        self.error_box._impl.native.classList.remove("active")    

    def show_error(self, error):
        self.error_label.text = error
        self.error_box._impl.native.classList.add("active")



class Logout(Dialog):
    def __init__(self):
        super().__init__(
            title="Logout"
        )

        cancel_label = toga.Label(
            id="logout_cancel_label",
            text="Stay"
        )

        self.cancel_button = toga.Box(
            id="logout_cancel_button",
            style=Pack(
                direction=ROW
            )
        )

        confirm_label = toga.Label(
            id="logout_confirm_label",
            text="Logout"
        )

        self.confirm_button = toga.Box(
            id="logout_confirm_button",
            style=Pack(
                direction=ROW
            )
        )

        buttons_box = toga.Box(
            id="logout_buttons_box",
            style=Pack(
                direction=ROW
            )
        )

        dialog_box = toga.Box(
            id="logout_dialog",
            style=Pack(
                direction=COLUMN
            )
        )

        self.add(
            dialog_box._impl.native
        )

        dialog_box.add(
            buttons_box
        )
        buttons_box.add(
            self.cancel_button,
            self.confirm_button
        )
        self.cancel_button.add(
            cancel_label
        )
        self.confirm_button.add(
            confirm_label
        )



class Password(Dialog):
    def __init__(self, type="login", name=""):
        super().__init__(
            closable=False
        )

        self.type = type

        self._on_confirm = None
        self.is_degit = False
        self.is_old_degit = False

        self.placeholder = "Password"
        if type == "create":
            self.set_title("Create Password")
        elif type == "login":
            self.set_icon("person-circle")
            self.set_title(f"{name}")
        elif type == "update":
            self.set_title("Update Password")
            self.placeholder = "New Password"

        self.error_label = toga.Label(
            id="password_error_label",
            text=""
        )

        self.error_box = toga.Box(
            id="password_error_box",
            style=Pack(
                direction=ROW
            )
        )

        self.old_password_input = toga.PasswordInput(
            placeholder="Current Password",
            on_change=self.on_password_change
        )
        self.old_password_input._impl.native.autocomplete="off"
        self.old_password_input._impl.native.autocapitalize="off"
        self.old_password_input._impl.native.autocorrect="off"
        self.old_password_input._impl.native.spellcheck="false"
        self.old_password_input._impl.native.passwordToggle = True
        self.old_password_input_prefix = create_element(
            "sl-icon",
            name="alphabet-uppercase",
            slot="prefix",
            classes=["password_input_prefix_icon"]
        )
        self.old_password_input_prefix.onclick = self.switch_old_input_mode
        self.old_password_input._impl.native.appendChild(
            self.old_password_input_prefix
        )

        self.password_input = toga.PasswordInput(
            placeholder=self.placeholder,
            on_change=self.on_password_change
        )
        self.password_input._impl.native.autocomplete="off"
        self.password_input._impl.native.autocapitalize="off"
        self.password_input._impl.native.autocorrect="off"
        self.password_input._impl.native.spellcheck="false"
        self.password_input._impl.native.passwordToggle = True
        self.password_input_prefix = create_element(
            "sl-icon",
            name="alphabet-uppercase",
            slot="prefix",
            classes=["password_input_prefix_icon"]
        )
        self.password_input_prefix.onclick = self.switch_input_mode
        self.password_input._impl.native.appendChild(
            self.password_input_prefix
        )
        self.keydown_listener = create_proxy(self._on_confirm_keydown)
        self.password_input._impl.native.addEventListener(
            "keydown",
            self.keydown_listener
        )

        self.name_input = toga.TextInput(
            placeholder="Name (optional)"
        )
        self.name_input._impl.native.autocomplete="off"

        cancel_label = toga.Label(
            id="password_cancel_label",
            text="Cancel"
        )

        self.cancel_button = toga.Box(
            id="password_cancel_button",
            style=Pack(
                direction=ROW
            )
        )

        confirm_label = toga.Label(
            id="password_confirm_label",
            text="Confirm"
        )

        self.confirm_button = toga.Box(
            id="password_confirm_button",
            style=Pack(
                direction=ROW
            )
        )

        buttons_box = toga.Box(
            id="password_buttons_box",
            style=Pack(
                direction=ROW
            )
        )

        timer_note = toga.Label(
            id="password_timer_note",
            text="Remember password temporarily"
        )

        self.timer_slider = toga.Slider(
            value=0,
            tick_count=7,
            min=0,
            max=30,
            style=Pack(
                flex=1
            )
        )
        self.timer_slider._impl.native.tooltipFormatter = create_proxy(self.tooltip_formatter)

        timer_box = toga.Box(
            id="password_timer_box",
            style=Pack(
                direction=COLUMN
            )
        )

        dialog_box = toga.Box(
            id="password_dialog",
            style=Pack(
                direction=COLUMN
            )
        )

        self.add(
            dialog_box._impl.native
        )
        if type == "create":
            dialog_box.add(self.name_input)
        elif type == "update":
            dialog_box.add(self.old_password_input)

        dialog_box.add(
            self.error_box,
            self.password_input
        )
        if type == "login":
            dialog_box.add(timer_box)
        dialog_box.add(
            buttons_box
        )
        buttons_box.add(
            self.cancel_button,
            self.confirm_button
        )
        self.cancel_button.add(
            cancel_label
        )
        self.confirm_button.add(
            confirm_label
        )
        timer_box.add(
            timer_note,
            self.timer_slider
        )
        self.error_box.add(
            self.error_label
        )


    def tooltip_formatter(self, value):
        return f"{value} mins"


    def switch_input_mode(self, event):
        self.password_input.value = ""
        if not self.is_degit:
            self.password_input_prefix.setAttribute("name", "123")
            self.password_input._impl.native.setAttribute("inputmode", "numeric")
            self.password_input._impl.native.maxlength="6"
            self.password_input._impl.native.minlength="6"
            self.password_input.placeholder = "6-Digit"
            self.is_degit = True
            return
        self.password_input_prefix.setAttribute("name", "alphabet-uppercase")
        self.password_input._impl.native.setAttribute("inputmode", "text")
        self.password_input._impl.native.maxlength="none"
        self.password_input._impl.native.minlength="8"
        self.password_input.placeholder = self.placeholder    
        self.is_degit = False


    def switch_old_input_mode(self, event):
        if not self.is_old_degit:
            self.old_password_input_prefix.setAttribute("name", "123")
            self.old_password_input._impl.native.setAttribute("inputmode", "numeric")
            self.old_password_input._impl.native.maxlength="6"
            self.old_password_input._impl.native.minlength="6"
            self.old_password_input.placeholder = "Current 6-Digit"
            self.is_old_degit = True
            return
        self.old_password_input_prefix.setAttribute("name", "alphabet-uppercase")
        self.old_password_input._impl.native.setAttribute("inputmode", "numeric")
        self.old_password_input._impl.native.maxlength="none"
        self.old_password_input._impl.native.minlength="8"
        self.old_password_input.placeholder = "Current Password"
        self.is_old_degit = False
        


    def on_password_change(self, event):
        if self.is_degit:
            if not event.value.isdigit():
                event.value = ""


    def _on_confirm_keydown(self, event):
        if event.key == "Enter":
            if self._on_confirm:
                self._on_confirm(event)
        

    def show_error(self, error):
        self.error_label.text = error
        self.error_box._impl.native.classList.add("active")