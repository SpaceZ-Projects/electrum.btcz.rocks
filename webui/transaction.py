
import asyncio
from datetime import datetime
import toga
from toga.style.pack import Pack
from toga.constants import ROW, COLUMN
from toga_web.libs import create_element

from .util import normalize_tx, format_balance, clipboard_copy
from .widget import Drawer


class TXInfo(Drawer):
    def __init__(self, app:toga.App, tx):
        super().__init__(
            title="Transaction Details",
            placement="start",
            size="85%",
            border_radius="20px"
        )

        self.app = app

        self.txid = tx["txid"]
        height = tx.get("height")
        amount = tx["amount"]
        direction = tx["direction"]
        from_addresses = tx["from"]
        to_addresses = tx["to"]
        confirmations = tx.get("confirmations")
        time = tx.get("time")
        size = tx["size"]
        locktime = tx.get("locktime")
        fee = tx["fee"]

        if direction == "sent":
            d_icon = "upload"
            text = "To :"
            addresses = to_addresses

        elif direction == "received":
            d_icon = "download"
            text = "From :"
            addresses = from_addresses

        elif direction == "self":
            d_icon = "arrow-repeat"
            text = "Self Transaction"
            addresses = [self.app.wallet.address]

        if confirmations == 0 or not time:
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            date = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

        txid_label = toga.Label(
            id="txinfo_txid_label",
            text=self.txid
        )

        copy_icon = create_element(
            "sl-icon",
            id="txinfo_copy_icon",
            name="clipboard2"
        )
        copy_icon.onclick = self.on_copy_txid

        txid_box = toga.Box(
            id="txinfo_txid_box",
            style=Pack(
                direction=ROW
            )
        )

        amount_label = toga.Label(
            id="txinfo_amount_label",
            text=f"Amount :"
        )
        
        amount_value = toga.Label(
            id="txinfo_amount_value",
            text=format_balance(amount)
        )

        amount_box = toga.Box(
            id="txinfo_amount_box",
            style=Pack(
                direction=ROW,
                flex=1
            )
        )

        direction_icon = create_element(
            "sl-icon",
            classes=["transaction_direction_icon"],
            name=d_icon
        )
        direction_icon.classList.add(direction)

        direction_label = toga.Label(
            id="txinfo_direction_label",
            text=direction.capitalize()
        )

        direction_box = toga.Box(
            id="txinfo_direction_box",
            style=Pack(
                direction=ROW
            )
        )

        fee_icon = create_element(
            "sl-icon",
            id="txinfo_fee_icon",
            name="fuel-pump"
        )

        fee_label = toga.Label(
            id="txinfo_fee_label",
            text=f"Fee : {format_balance(fee)}"
        )

        fee_box = toga.Box(
            id="txinfo_fee_box",
            style=Pack(
                direction=ROW
            )
        )

        size_icon = create_element(
            "sl-icon",
            id="txinfo_size_icon",
            name="database"
        )

        size_label = toga.Label(
            id="txinfo_size_label",
            text=f"Size : {size} bytes"
        )

        size_box = toga.Box(
            id="txinfo_size_box",
            style=Pack(
                direction=ROW
            )
        )

        confirmations_icon = create_element(
            "sl-icon",
            id="txinfo_confirmations_icon",
            name="check2-circle"
        )

        self.confirmations_label = toga.Label(
            id="txinfo_confirmations_label",
            text=f"Confirmations : {confirmations}"
        )

        confirmations_box = toga.Box(
            id="txinfo_confirmations_box",
            style=Pack(
                direction=ROW
            )
        )

        time_icon = create_element(
            "sl-icon",
            id="txinfo_time_icon",
            name="calendar3"
        )

        self.time_label = toga.Label(
            id="txinfo_time_label",
            text=f"Date : {date}"
        )

        time_box = toga.Box(
            id="txinfo_time_box",
            style=Pack(
                direction=ROW
            )
        )

        locktime_icon = create_element(
            "sl-icon",
            id="txinfo_locktime_icon",
            name="lock"
        )

        locktime_label = toga.Label(
            id="txinfo_locktime_label",
            text=f"Locktime : {locktime}"
        )

        locktime_box = toga.Box(
            id="txinfo_locktime_box",
            style=Pack(
                direction=ROW
            )
        )

        height_icon = create_element(
            "sl-icon",
            id="txinfo_height_icon",
            name="boxes"
        )

        self.height_label = toga.Label(
            id="txinfo_height_label",
            text=f"Height : {height}"
        )

        height_box = toga.Box(
            id="txinfo_height_box",
            style=Pack(
                direction=ROW
            )
        )

        address_label = toga.Label(
            id="txinfo_address_label",
            text=text
        )

        addresses_list = toga.Box(
            id="txinfo_addresses_list",
            style=Pack(
                direction=COLUMN
            )
        )

        addresses_box = toga.Box(
            id="txinfo_addresses_box"
        )

        drawer_box = toga.Box(
            id="txinfo_drawer_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.add(
            drawer_box._impl.native
        )
        drawer_box.add(
            txid_box,
            direction_box,
            fee_box,
            size_box,
            confirmations_box,
            time_box,
            locktime_box,
            height_box,
            addresses_box
        )
        txid_box.add(
            txid_label
        )
        txid_box._impl.native.appendChild(
            copy_icon
        )
        direction_box.add(
            amount_box
        )
        direction_box._impl.native.appendChild(
            direction_icon
        )
        direction_box.add(
            direction_label
        )
        amount_box.add(
            amount_label,
            amount_value
        )
        fee_box._impl.native.appendChild(
            fee_icon
        )
        fee_box.add(
            fee_label
        )
        size_box._impl.native.appendChild(
            size_icon
        )
        size_box.add(
            size_label
        )
        confirmations_box._impl.native.appendChild(
            confirmations_icon
        )
        confirmations_box.add(
            self.confirmations_label
        )
        time_box._impl.native.appendChild(
            time_icon
        )
        time_box.add(
            self.time_label
        )
        locktime_box._impl.native.appendChild(
            locktime_icon
        )
        locktime_box.add(
            locktime_label
        )
        height_box._impl.native.appendChild(
            height_icon
        )
        height_box.add(
            self.height_label
        )
        addresses_box.add(
            address_label,
            addresses_list
        )

        for addr in addresses:
            address_widget = toga.Label(
                    text=addr
            )
            address_widget._impl.native.className = "txinfo_address_widget"
            addresses_list._impl.native.appendChild(address_widget._impl.native)



    def on_copy_txid(self, event):
        clipboard_copy(self.txid)

    
    def update_info(self):
        self.app.loop.create_task(self.get_tx_info())

    async def get_tx_info(self):
        try:
            result = await self.app.client.get_transaction(self.txid)
            tx = normalize_tx(result, self.app.wallet.address)
            height = tx.get("height")
            confirmations = tx.get("confirmations")
            time = tx.get("time")
            date = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

            self.height_label.text = f"Height : {height}"
            self.confirmations_label.text = f"Confirmations : {confirmations}"
            self.time_label.text = f"Date : {date}"
        except Exception:
            pass



class Transaction(toga.Box):
    def __init__(self, app:toga.App, data):
        super().__init__(
            id= "home_transaction_box",
            style=Pack(
                direction=ROW
            )
        )

        self.app = app

        tx = normalize_tx(data, self.app.wallet.address)
        self.txid = tx["txid"]

        amount = tx["amount"]
        direction = tx["direction"]
        confirmations = tx.get("confirmations", 0)
        time = tx.get("time")

        sign = "-" if direction == "sent" else "+" if direction == "received" else ""
        fiat = amount * self.app.price

        if confirmations == 0 or not time:
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            date = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

        if confirmations <= 0:
            c_icon = "0"
        elif confirmations == 1:
            c_icon = "1"
        elif confirmations == 2:
            c_icon = "2"
        elif confirmations == 3:
            c_icon = "3"
        else:
            c_icon = "4"

        if direction == "sent":
            d_icon = "upload"

        elif direction == "received":
            d_icon = "download"

        elif direction == "self":
            d_icon = "arrow-repeat"

        direction_icon = create_element(
            "sl-icon",
            classes=["transaction_direction_icon"],
            name=d_icon
        )
        direction_icon.classList.add(direction)

        self.confirmations_icon = create_element(
            "sl-icon",
            classes=["transaction_confirmations_icon"],
            name=f"reception-{c_icon}"
        )

        btcz_icon = create_element(
            "sl-icon",
            classes=["transaction_btcz_icon"],
            name="btcz"
        )

        amount_label = toga.Label(
            text=f"{format_balance(amount)}"
        )
        amount_label._impl.native.className = "transaction_amount_label"

        amount_box = toga.Box(
            style=Pack(
                direction=ROW
            )
        )
        amount_box._impl.native.className = "transaction_amount_box"

        fiat_label = toga.Label(
            text=f"{sign} ${fiat:.2f}"
        )
        fiat_label._impl.native.className = "transaction_fiat_label"
        fiat_label._impl.native.classList.add(direction)

        fiat_box = toga.Box(
            style=Pack(
                direction=ROW
            )
        )
        fiat_box._impl.native.className = "transaction_fiat_box"

        time_icon = create_element(
            "sl-icon",
            classes=["transaction_time_icon"],
            name="calendar3"
        )

        self.time_label = toga.Label(
            text=date
        )
        self.time_label._impl.native.className = "transaction_time_label"

        time_box = toga.Box(
            style=Pack(
                direction=ROW
            )
        )
        time_box._impl.native.className = "transaction_time_box"

        self._impl.native.appendChild(
            direction_icon
        )
        self._impl.native.appendChild(
            self.confirmations_icon
        )
        self.add(
            amount_box,
            fiat_box,
            time_box
        )
        amount_box._impl.native.appendChild(btcz_icon)
        amount_box.add(
            amount_label
        )
        fiat_box.add(
            fiat_label
        )
        time_box._impl.native.appendChild(
            time_icon
        )
        time_box.add(
            self.time_label
        )


    def update_transaction(self):
        self.app.loop.create_task(self.update_confirmations())
    
    async def update_confirmations(self):
        tx = await self.app.client.get_transaction(self.txid)
        confirmations = tx.get("confirmations")
        time = tx.get("time")
        try:
            if confirmations <= 0:
                c_icon = "0"
            elif confirmations == 1:
                c_icon = "1"
            elif confirmations == 2:
                c_icon = "2"
            elif confirmations == 3:
                c_icon = "3"
            else:
                c_icon = "4"
            self.confirmations_icon.setAttribute(
                "name",
                f"reception-{c_icon}"
            )
            if time:
                date = date = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
                self.time_label.text = date
        except Exception:
            pass


    def pulse(self):
        self.app.loop.create_task(self._pulse())

    async def _pulse(self):
        try:
            await asyncio.sleep(0.2)
            self._impl.native.classList.add("pulse")
            await asyncio.sleep(0.4)
            self._impl.native.classList.remove("pulse")
        except Exception:
            pass

    