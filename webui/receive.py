
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW
from toga_web.libs import create_element

from .util import format_address, clipboard_copy


class Receive(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "receive_page",
            style=Pack(
                direction=COLUMN,
                flex=1
            )
        )

        self.app = app

        self.qr_code = create_element(
            "sl-qr-code",
            id="receive_qr_code",
            value="",
            size=280
        )

        qr_code_box = toga.Box(
            id="receive_qr_code_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.address_label = toga.Label(
            id="receive_address_label",
            text=""
        )

        copy_icon = create_element(
            "sl-icon",
            id="receive_copy_icon",
            name="clipboard2"
        )
        copy_label = toga.Label(
            id="receive_copy_label",
            text="Copy"
        )

        self.copy_button = toga.Box(
            id="receive_copy_button",
            style=Pack(
                direction=ROW
            )
        )
        self.copy_button._impl.native.onclick = self.on_copy_click

        self.add(
            qr_code_box,
            self.address_label,
            self.copy_button
        )
        qr_code_box._impl.native.appendChild(self.qr_code)
        self.copy_button._impl.native.appendChild(
            copy_icon
        )
        self.copy_button.add(
            copy_label
        )


    def show_qr_code(self):
        self.qr_code.value = self.app.wallet.address
        self.address_label.text = format_address(self.app.wallet.address)

    def on_copy_click(self, event):
        clipboard_copy(self.app.wallet.address)