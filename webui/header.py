
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW
from toga_web.libs import create_element

from .util import format_balance, format_price
from .widget import Tooltip, Alert


class Header(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "page_header",
            style=Pack(
                direction=COLUMN,
                flex=1
            )
        )

        self.app = app

        self.electrum_status_box = None

        self.status_icon = create_element(
            "sl-icon",
            classes=["status_icon"],
            name="circle-fill"
        )

        electrum_height_icon = create_element(
            "sl-icon",
            classes=["electrum_height_icon"],
            name="boxes"
        )

        self.electrum_height_value = toga.Label(
            text=""
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

        donation_button_icon = create_element(
            "sl-icon",
            id="header_donation_button_icon",
            name="heart"
        )

        donation_button_label = toga.Label(
            id="header_donation_button_label",
            text="Donate"
        )

        donation_button = toga.Box(
            id="header_donation_button",
            style=Pack(
                direction=ROW
            )
        )
        Tooltip(text="Donate to electrum server", duration=3000, position="bottom").attach_to(
            donation_button._impl.native
        )
        donation_button._impl.native.onclick = self.on_donation_click

        status_box = toga.Box(
            id="header_status_box",
            style=Pack(
                direction=ROW
            )
        )

        account_icon = create_element(
            "sl-icon",
            id="header_account_icon",
            name="person-circle"
        )

        self.account_name = toga.Label(
            id="header_account_name",
            text=""
        )

        account_box = toga.Box(
            id="header_account_box",
            style=Pack(
                direction=ROW
            )
        )

        balance_label = toga.Label(
            id="header_balance_label",
            text="Balance"
        )

        self.confirmed_balance = toga.Label(
            id="header_confirmed_balance",
            text="0.00000000"
        )

        self.unconfirmed_balance = toga.Label(
            id="header_unconfirmed_balance",
            text="0.00000000"
        )

        self.price_value = toga.Label(
            id="header_price_value",
            text="$0.00"
        )

        balance_box = toga.Box(
            id="header_balance_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.add(
            status_box,
            balance_box
        )
        status_box._impl.native.appendChild(
            self.status_icon
        )
        status_box._impl.native.appendChild(
            electrum_height_icon
        )
        status_box.add(
            self.electrum_height_value,
            self.electrum_version_value,
            self.electrum_protocol_value,
            donation_button
        )
        donation_button._impl.native.appendChild(
            donation_button_icon
        )
        donation_button.add(
            donation_button_label
        )
        balance_box.add(
            self.price_value,
            account_box,
            balance_label,
            self.confirmed_balance,
            self.unconfirmed_balance
        )
        account_box._impl.native.appendChild(
            account_icon
        )
        account_box.add(
            self.account_name
        )


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
        Tooltip(text=self.app.client.url, duration=3000, position="bottom").attach_to(self.status_icon)


    async def update_balance(self):
        try:
            result = await self.app.client.get_balance(self.app.wallet.address)
            confirmed = result["confirmed"]
            unconfirmed = result["unconfirmed"]
            balance = confirmed + unconfirmed
            balance_str = balance / 1e8
            self.confirmed_balance.text = f"{format_balance(balance_str)}"
            if unconfirmed == 0:
                self.unconfirmed_balance._impl.native.classList.remove("positive")
                self.unconfirmed_balance._impl.native.classList.remove("negative")
            else:
                unconfirmed_str = unconfirmed / 1e8
                sign = "+" if unconfirmed > 0 else "-"
                self.unconfirmed_balance.text = (
                    f"{sign}{format_balance(abs(unconfirmed_str))}"
                )
                if unconfirmed > 0:
                    self.unconfirmed_balance._impl.native.classList.remove("negative")
                    self.unconfirmed_balance._impl.native.classList.add("positive")
                else:
                    self.unconfirmed_balance._impl.native.classList.remove("positive")
                    self.unconfirmed_balance._impl.native.classList.add("negative")
            self.app.balance = balance
            
        except Exception:
            pass


    def update_price(self, price):
        self.price_value.text = f"1BTCZ = ${format_price(price)}"


    async def get_server_donation_address(self):
        try:
            address = await self.app.client.get_donation_address()
            if address == "":
                Alert().show("No donation address for this server", variant="warning")
                return
            print(address)
        except Exception:
            Alert().show("Failed to get donation address", variant="danger")
            


    def on_donation_click(self, event):
        self.app.loop.create_task(self.get_server_donation_address())