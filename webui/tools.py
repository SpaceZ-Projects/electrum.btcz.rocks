
import asyncio
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW
from toga_web.libs import create_element

from .dialog import Password
from .widget import Textarea


class Tools(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "tools_page",
            style=Pack(
                direction=COLUMN,
                flex=1
            )
        )

        self.app = app

        self.verify_trigger = False
        self.sign_trigger = False
        self.active_box = None

        self.password_dialog = None


        verify_tab_icon = create_element(
            "sl-icon",
            id="tools_verify_tab_icon",
            name="check2-circle"
        )
        verify_tab_label = toga.Label(
            id="tools_verify_tab_label",
            text="Verify Message"
        )
        self.verify_tab = toga.Box(
            id="tools_verify_tab",
            style=Pack(
                direction=ROW
            )
        )
        self.verify_tab._impl.native.onclick = self.on_verify_click

        sign_tab_icon = create_element(
            "sl-icon",
            id="tools_sign_tab_icon",
            name="pen"
        )
        sign_tab_label = toga.Label(
            id="tools_sign_tab_label",
            text="Sign Message"
        )
        self.sign_tab = toga.Box(
            id="tools_sign_tab",
            style=Pack(
                direction=ROW
            )
        )
        self.sign_tab._impl.native.onclick = self.on_sign_click

        switch_box = toga.Box(
            id="tools_switch_box",
            style=Pack(
                direction=ROW
            )
        )

        verify_message_label = toga.Label(
            id="tools_verify_message_label",
            text="Message :"
        )

        self.verify_message_input = Textarea(
            placeholder="Enter message to verify",
            rows=3,
            required=True,
            resize="none",
            on_input=self.on_verify_message_change
        )

        verify_message_box = toga.Box(
            id="tools_verify_message_box",
            style=Pack(
                direction=ROW
            )
        )

        verify_address_label = toga.Label(
            id="tools_verify_address_label",
            text="Address :"
        )

        self.verify_address_input = toga.TextInput(
            placeholder="Enter address",
            on_change=self.on_verify_address_change
        )
        self.verify_address_input._impl.native.autocomplete="off"

        verify_address_box = toga.Box(
            id="tools_verify_address_box",
            style=Pack(
                direction=ROW
            )
        )

        verify_signature_label = toga.Label(
            id="tools_verify_signature_label",
            text="Signature :"
        )

        self.verify_signature_input = Textarea(
            placeholder="Enter signature",
            rows=3,
            required=True,
            resize="none",
            on_input=self.on_verify_message_change
        )

        verify_signature_box = toga.Box(
            id="tools_verify_signature_box",
            style=Pack(
                direction=ROW
            )
        )

        self.verify_box = toga.Box(
            id="tools_verify_box",
            style=Pack(
                direction=COLUMN
            )
        )

        sign_message_label = toga.Label(
            id="tools_sign_message_label",
            text="Message :"
        )

        self.sign_message_input = Textarea(
            placeholder="Enter message to sign",
            rows=3,
            required=True,
            resize="none",
            on_input=self.on_sign_message_change
        )

        sign_message_box = toga.Box(
            id="tools_sign_message_box",
            style=Pack(
                direction=ROW
            )
        )

        self.limit_value = toga.Label(
            id="tools_limit_value",
            text="0/200"
        )

        limit_box = toga.Box(
            id="tools_limit_box",
            style=Pack(
                direction=ROW
            )
        )

        self.sign_box = toga.Box(
            id="tools_sign_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.result_input = Textarea(
            readonly=True,
            rows=3,
            resize="none",
        )

        self.result_box = toga.Box(
            id="tools_result_box",
            style=Pack(
                direction=ROW
            )
        )

        self.tools_button_label = toga.Label(
            id="tools_button_label",
            text="Verify"
        )

        self.tools_button = toga.Box(
            id="tools_button",
            style=Pack(
                direction=ROW
            )
        )
        self.tools_button._impl.native.onclick = self.on_confirm_click

        self.tools_button_box = toga.Box(
            id="tools_button_box"
        )

        self.add(
            switch_box,
            self.verify_box,
            self.sign_box,
            self.result_box,
            self.tools_button_box
        )
        switch_box.add(
            self.verify_tab,
            self.sign_tab
        )
        self.verify_tab._impl.native.appendChild(
            verify_tab_icon
        )
        self.verify_tab.add(
            verify_tab_label
        )
        self.sign_tab._impl.native.appendChild(
            sign_tab_icon
        )
        self.sign_tab.add(
            sign_tab_label
        )
        self.verify_box.add(
            verify_message_box,
            verify_address_box,
            verify_signature_box
        )
        verify_message_box.add(
            verify_message_label
        )
        verify_address_box.add(
            verify_address_label,
            self.verify_address_input
        )
        verify_signature_box.add(
            verify_signature_label
        )
        self.verify_message_input.attach_to(verify_message_box._impl.native)
        self.verify_signature_input.attach_to(verify_signature_box._impl.native)
        self.sign_box.add(
            sign_message_box,
            limit_box
        )
        sign_message_box.add(
            sign_message_label
        )
        self.sign_message_input.attach_to(sign_message_box._impl.native)
        limit_box.add(
            self.limit_value
        )
        self.result_input.attach_to(self.result_box._impl.native)
        self.tools_button_box.add(
            self.tools_button
        )
        self.tools_button.add(
            self.tools_button_label
        )

        self.set_default_tab()


    def set_default_tab(self):
        self.set_verify_tab()

    async def tabs_transition(self, active_tab, active_box):
        tabs = [
            self.verify_tab,
            self.sign_tab
        ]
        for tab in tabs:
            tab._impl.native.classList.remove("active")
        if self.active_box:
            self.active_box._impl.native.classList.remove("active")
            await asyncio.sleep(0.2)
            self.active_box._impl.native.classList.remove("show")
        active_box._impl.native.classList.add('show')
        active_tab._impl.native.classList.add("active")

        await asyncio.sleep(0.2)
        active_box._impl.native.classList.add('active')
        self.active_box = active_box

    def set_active(self, active_tab, active_box):
        self.verify_trigger = False
        self.sign_trigger = False
        self.hide_result()
        self.clean_inputs()
        self.app.loop.create_task(self.tabs_transition(active_tab, active_box))


    def set_verify_tab(self):
        if not self.verify_trigger:
            self.set_active(self.verify_tab, self.verify_box)
            self.verify_trigger = True


    def set_sign_tab(self):
        if not self.sign_trigger:
            self.set_active(self.sign_tab, self.sign_box)
            self.sign_trigger = True


    def on_verify_click(self, event):
        self.set_verify_tab()
        self.tools_button_label.text = "Verify"

    def on_sign_click(self, event):
        self.set_sign_tab()
        self.tools_button_label.text = "Sign"

    def is_filled(self):
        message = self.verify_message_input.value.strip()
        address = self.verify_address_input.value.strip()
        signature = self.verify_signature_input.value.strip()
        if not message or not address or not signature:
            return False
        return True

    def on_verify_message_change(self, event):
        if not self.is_filled():
            self.tools_button._impl.native.classList.remove("active")
            self.hide_result()
            return
        self.tools_button._impl.native.classList.add("active")

    def on_verify_address_change(self, event):
        address = self.verify_address_input.value.strip()
        if not address:
            self.verify_address_input._impl.native.classList.remove("error")
        else:
            from btczpy.crypto import is_address
            if not is_address(address):
                self.verify_address_input._impl.native.classList.add("error")
            else:
                self.verify_address_input._impl.native.classList.remove("error")
        if not self.is_filled():
            self.tools_button._impl.native.classList.remove("active")
            self.hide_result()
            return
        self.tools_button._impl.native.classList.add("active")


    def on_sign_message_change(self, event):
        message = self.sign_message_input.value.strip()
        if not message:
            self.limit_value.text = "0/200"
            self.tools_button._impl.native.classList.remove("active")
            self.hide_result()
            return
        self.tools_button._impl.native.classList.add("active")
        count = len(message)
        if count > 200:
            self.limit_value._impl.native.classList.add("error")
        else:
            self.limit_value._impl.native.classList.remove("error")
        self.limit_value.text = f"{len(message)}/200"


    def on_confirm_click(self, event):
        if self.sign_trigger:
            message = self.sign_message_input.value.strip()
            if not message:
                return
            count = len(message)
            if count > 200:
                return
            if self.app.wallet.is_unlocked():
                signed_message = self.sign_message(message)
                if not signed_message:
                    self.result_input.value = "Signing message failed"
                    self.show_error()
                    return
                self.result_input.value = signed_message
                self.show_success()
                return
            self.password_dialog = Password(name=self.app.wallet.name)
            self.password_dialog.confirm_button._impl.native.onclick = self.on_confirm_sign
            self.password_dialog.cancel_button._impl.native.onclick = self.on_cancel_sign
            self.password_dialog.show()
        else:
            import base64
            from btczpy.crypto import verify_message, is_address
            message = self.verify_message_input.value.strip()
            address = self.verify_address_input.value.strip()
            signature = self.verify_signature_input.value.strip()
            if not message or not address or not signature:
                return
            sig = None
            if not is_address(address):
                self.result_input.value = "Invalid address"
                self.show_error()
            else:
                try:
                    sig = base64.b64decode(signature)
                except Exception:
                    sig = None
                    self.result_input.value = "Invalid base64 signature"
                    self.show_error()
            if sig:
                try:
                    valid = verify_message(
                        address,
                        signature,
                        message.encode()
                    )
                    if valid is True:
                        self.result_input.value = "Valid"
                        self.show_success()
                    else:
                        self.result_input.value = "Invalid"
                        self.show_error()
                except Exception as e:
                    self.result_input.value = "Verfication message failed"
                    self.show_error()
            self.app.main_window.scroll_pages_to_bottom()


    def on_confirm_sign(self, event):
        password = self.password_dialog.password_input.value.strip()
        if not password:
            return
        message = self.sign_message_input.value.strip()
        signed_message = self.sign_message(message, password)
        if not signed_message:
            self.result_input.value = "Signing message failed"
            self.show_error()
            return
        self.show_success()
        self.result_input.value = signed_message
        timer = self.password_dialog.timer_slider.value
        if timer > 0:
            self.app.wallet.cache_password(password, timer)
        self.password_dialog.hide()
        self.password_dialog = None

    def sign_message(self, message, password=None):
        try:
            return self.app.wallet.sign_message(message, password)
        except Exception:
            return None
        

    def on_cancel_sign(self, event):
        self.password_dialog.hide()
        self.password_dialog = None


    def clean_inputs(self):
        self.tools_button._impl.native.classList.remove("active")
        self.verify_message_input.value = ""
        self.verify_address_input.value = ""
        self.verify_address_input._impl.native.classList.remove("error")
        self.verify_signature_input.value = ""
        self.sign_message_input.value = ""
        

    def hide_result(self):
        self.result_box._impl.native.classList.remove("active")

    def show_error(self):
        self.result_box._impl.native.classList.remove("success")
        self.result_box._impl.native.classList.add("error")
        self.result_box._impl.native.classList.add("active")

    def show_success(self):
        self.result_box._impl.native.classList.remove("error")
        self.result_box._impl.native.classList.add("success")
        self.result_box._impl.native.classList.add("active")

    def on_resize(self, value):
        if value == "mobile":
            self.tools_button_box._impl.native.classList.add("mobile")
        elif value == "desktop":
            self.tools_button_box._impl.native.classList.remove("mobile")