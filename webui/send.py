
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW
from toga_web.libs import create_element
from js import window
from pyodide.ffi import create_proxy

from .widget import Alert, Drawer
from .dialog import Password
from .util import format_balance, normalize_tx
from .transaction import TXInfo


class QRScanner(Drawer):
    def __init__(self):
        super().__init__(
            title="QR Scanner",
            placement="top",
            size="fit-content",
            border_radius="20px"
        )

        qr_scanner_box = toga.Box(
            id="qr_scanner",
            style=Pack(
                direction=COLUMN
            )
        )

        self.add(
            qr_scanner_box._impl.native
        )



class Broadcast(Drawer):
    def __init__(self, destination, amount, fee):
        super().__init__(
            title="Broadcast Transaction",
            placement="bottom",
            size="fit-content",
            border_radius="20px"
        )

        self.destination = destination
        self.amount = amount
        self.fee = fee

        amount_str = amount / 1e8

        destination_label = toga.Label(
            id="broadcast_destination_label",
            text=f"To : {destination}"
        )

        amount_label = toga.Label(
            id="broadcast_amount_label",
            text=f"Amount : {format_balance(amount_str)}"
        )

        fee_label = toga.Label(
            id="broadcast_fee_label",
            text=f"Fee : {(fee / 1e8):.8f}"
        )

        broadcast_box = toga.Box(
            id="broadcast_box",
            style=Pack(
                direction=COLUMN
            )
        )

        send_icon = create_element(
            "sl-icon",
            id="broadcast_confirm_icon",
            name="send"
        )

        confirm_label = toga.Label(
            id="broadcast_confirm_label",
            text="Broadcast"
        )

        self.confirm_button = toga.Box(
            id="broadcast_confirm_button",
            style=Pack(
                direction=ROW
            )
        )

        self.drawer_box = toga.Box(
            id="broadcast_drawer_box",
            style=Pack(
                direction=COLUMN
            )
        )

        success_icon = create_element(
            "sl-icon",
            id="broadcast_success_icon",
            name="check-circle-fill"
        )

        sucess_label = toga.Label(
            id="broadcast_success_label",
            text="Transaction Sent"
        )

        view_button_label = toga.Label(
            id="broadcast_view_label",
            text="View TX"
        )

        self.view_button = toga.Box(
            id="broadcast_view_button",
            style=Pack(
                direction=ROW
            )
        )
        
        self.result_box = toga.Box(
            id="broadcast_result_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.add(
            self.drawer_box._impl.native,
            self.result_box._impl.native
        )
        self.drawer_box.add(
            broadcast_box,
            self.confirm_button
        )
        broadcast_box.add(
            destination_label,
            amount_label,
            fee_label
        )
        self.confirm_button._impl.native.appendChild(
            send_icon
        )
        self.confirm_button.add(
            confirm_label
        )
        self.result_box._impl.native.appendChild(
            success_icon
        )
        self.result_box.add(
            sucess_label,
            self.view_button
        )
        self.view_button.add(
            view_button_label
        )


    def show_success(self):
        self.no_header = True
        self.drawer_box._impl.native.classList.add("hide")
        self.result_box._impl.native.classList.add("show")



class Send(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "send_page",
            style=Pack(
                direction=COLUMN,
                flex=1
            )
        )

        self.app = app

        self.qr_drawer = None
        self.broadcast_drawer = None
        self.password_dialog = None
        self.is_fiat = False
        self.tx_drawer = None

        self.manual_fee = True

        destination_label = toga.Label(
            id="send_destination_label",
            text="To address :"
        )

        self.destination_input = toga.TextInput(
            placeholder="Enter address",
            style=Pack(
                flex=1
            ),
            on_change=self.on_destination_change
        )
        self.destination_input._impl.native.autocomplete="off"

        qr_button = create_element(
            "sl-icon",
            id="send_qr_button",
            name="qr-code-scan"
        )
        qr_button.onclick = self.on_qr_scanner_click

        destination_input_box = toga.Box(
            id="send_destination_input_box",
            style=Pack(
                direction=ROW
            )
        )

        destination_box = toga.Box(
            id="send_destination_box",
            style=Pack(
                direction=ROW
            )
        )

        amount_label = toga.Label(
            id="send_amount_label",
            text="Amount :"
        )

        self.amount_input = toga.TextInput(
            placeholder="0.00000000",
            on_change=self.on_amount_change
        )
        self.amount_input._impl.native.type = "number"
        self.amount_input._impl.native.autocomplete="off"
        self.amount_input_prefix = create_element(
            "sl-icon",
            name="btcz",
            slot="prefix",
            classes=["amount_input_prefix_icon"]
        )
        self.amount_input._impl.native.appendChild(
            self.amount_input_prefix
        )
        self.amount_input_prefix.onclick = self.switch_to_fiat

        max_button_label = toga.Label(
            id="send_max_button_label",
            text="Max"
        )

        max_button = toga.Box(
            id="send_max_button",
            style=Pack(
                direction=ROW
            )
        )
        max_button._impl.native.onclick = self.on_max_click

        amount_input_box = toga.Box(
            id="send_amount_input_box",
            style=Pack(
                direction=ROW
            )
        )

        amount_box = toga.Box(
            id="send_amount_box",
            style=Pack(
                direction=ROW
            )
        )

        fee_label = toga.Label(
            id="send_fee_label",
            text="Fee :"
        )

        self.fee_input = toga.TextInput(
            placeholder="0.00000000",
            value="0.00001000",
            on_change=self.on_fee_change
        )
        self.fee_input._impl.native.type = "number"
        self.fee_input._impl.native.autocomplete="off"

        fee_input_box = toga.Box(
            id="send_fee_input_box",
            style=Pack(
                direction=ROW
            )
        )

        fee_box = toga.Box(
            id="send_fee_box",
            style=Pack(
                direction=ROW
            )
        )

        self.send_button_label = toga.Label(
            id="send_button_label",
            text="Send"
        )

        self.send_button = toga.Box(
            id="send_button",
            style=Pack(
                direction=ROW
            )
        )
        self.send_button._impl.native.onclick = self.on_send_click

        self.send_button_box = toga.Box(
            id="send_button_box"
        )

        self.add(
            destination_box,
            amount_box,
            fee_box,
            self.send_button_box
        )
        destination_box.add(
            destination_label,
            destination_input_box
        )
        destination_input_box.add(
            self.destination_input
        )
        destination_input_box._impl.native.appendChild(
            qr_button
        )
        amount_box.add(
            amount_label,
            amount_input_box
        )
        amount_input_box.add(
            self.amount_input,
            max_button
        )
        max_button.add(
            max_button_label
        )
        fee_box.add(
            fee_label,
            fee_input_box
        )
        fee_input_box.add(
            self.fee_input
        )
        self.send_button_box.add(
            self.send_button
        )
        self.send_button.add(
            self.send_button_label
        )


    async def on_max_click(self, event):
        SAT_PER_BYTE = 1
        self.manual_fee = False
        utxos = await self.app.client.get_listunspent(self.app.wallet.address)
        if not utxos:
            return
        utxos.sort(key=lambda x: x["value"])

        selected = []
        total = 0

        for u in utxos:
            selected.append(u)
            total += u["value"]

        fee = (len(selected) * 148 + 2 * 34 + 10) * SAT_PER_BYTE
        amount_sat = total - fee
        if amount_sat <= 0:
            return

        amount_btcz = amount_sat / 1e8

        if self.is_fiat:
            if not self.app.price or self.app.price <= 0:
                return
            amount_fiat = amount_btcz * self.app.price
            amount_fiat *= 0.999999
            self.amount_input.value = f"{amount_fiat:.8f}"
        else:
            self.amount_input.value = format_balance(amount_btcz)

        self.fee_input.value = format_balance(fee / 1e8)
        self.on_amount_change(None)


    def show_qr_scanner(self):
        self.qr_drawer = QRScanner()
        self.qr_drawer.on_after_hide = self.on_qr_scanner_hide
        self.qr_drawer.on_request_close = self.on_qr_scanner_hide
        self.qr_drawer.show()

        def on_qr_scanned(data):
            scanned = data.strip()
            if scanned.startswith("bitcoinz:"):
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(scanned)
                address = parsed.path
                params = parse_qs(parsed.query)
                amount = params.get("amount", [None])[0]
                self.destination_input.value = address
                if amount:
                    self.amount_input.value = amount
                    self.on_amount_change(None)
            else:
                self.destination_input.value = scanned
            self.qr_drawer.hide()
            window.qr.stopQR()
            self.qr_drawer = None

        def on_qr_error(err):
            Alert().show(f"QRERROR: {err}", "warning")
            self.qr_drawer.hide()
            try:
                window.qr.stopQR()
            except Exception:
                pass
            self.qr_drawer = None

        window.on_qr_scanned = create_proxy(on_qr_scanned)
        window.on_qr_error = create_proxy(on_qr_error)
        window.qr.startQR()


    async def check_camera(self):
        result = await window.qr.checkCamera()
        if not result.ok:
            err = result.error
            if err == "no_camera":
                Alert().show("No camera found on this device", "warning")
            elif err == "NotAllowedError":
                Alert().show("Camera permission denied", "warning")
            elif err == "unsupported":
                Alert().show("Camera not supported", "warning")
            else:
                Alert().show("Camera error: " + str(err), "warning")
            return
        
        self.show_qr_scanner()

    def on_qr_scanner_click(self, event):
        self.app.loop.create_task(self.check_camera())
        

    def on_qr_scanner_hide(self, event):
        try:
            window.qr.stopQR()
        except Exception:
            pass
        self.qr_drawer = None


    def on_send_click(self, event):
        self.app.loop.create_task(self.verify_send())

    def clean_inputs(self):
        self.send_button._impl.native.classList.remove("active")
        self.destination_input.value = ""
        self.amount_input.value = ""
        self.fee_input.value = "0.00001000"

    def is_filled(self):
        destination = self.destination_input.value.strip()
        amount = self.amount_input.value.strip()
        if not destination or not amount:
            return False
        return True

    def on_destination_change(self, event):
        destination = self.destination_input.value.strip()
        if not destination:
            self.destination_input._impl.native.classList.remove("error")
        else:
            from btczpy.crypto import is_address
            if not is_address(destination):
                self.destination_input._impl.native.classList.add("error")
                self.send_button._impl.native.classList.remove("active")
                return
            else:
                self.destination_input._impl.native.classList.remove("error")
        if not self.is_filled():
            self.send_button._impl.native.classList.remove("active")
            return
        self.send_button._impl.native.classList.add("active")
        

    def on_amount_change(self, event):
        amount = self.amount_input.value.strip()
        if not amount:
            self.amount_input._impl.native.classList.remove("error")
            self.fee_input.value = "0.00001000"
            self.manual_fee = True
        else:
            try:
                value = float(amount)
            except ValueError:
                self.amount_input._impl.native.classList.add("error")
                pass
            balance_btcz = self.app.balance / 1e8
            if self.is_fiat:
                price = self.app.price
                balance_fiat = balance_btcz * price
                valid = value > 0 and value <= balance_fiat
            else:
                valid = value > 0 and value <= balance_btcz
            if valid:
                self.amount_input._impl.native.classList.remove("error")
            else:
                self.amount_input._impl.native.classList.add("error")
                self.send_button._impl.native.classList.remove("active")
                return
        if not self.is_filled():
            self.send_button._impl.native.classList.remove("active")
            return
        self.send_button._impl.native.classList.add("active")

    
    def switch_to_fiat(self, event):
        if self.is_fiat:
            self.amount_input_prefix.setAttribute("name", "btcz")
            self.amount_input.placeholder = "0.00000000"
            self.is_fiat = False
        else:
            self.amount_input_prefix.setAttribute("name", "currency-dollar")
            self.amount_input.placeholder = "0.00"
            self.is_fiat = True
        self.amount_input.value = ""


    def on_fee_change(self, event):
        self.manual_fee = True

    
    async def verify_send(self):
        destination = self.destination_input.value.strip()
        amount = self.amount_input.value.strip()
        fee = self.fee_input.value.strip()
        if not destination:
            Alert().show("Enter a destination address", "warning")
            return
        from btczpy.crypto import is_address
        if not is_address(destination):
            Alert().show("Invalid address format", "danger")
            return
        if not amount:
            Alert().show("Enter an amount", "warning")
            return
        try:
            amount = float(amount)
        except ValueError:
            Alert().show("Invalid amount format", "danger")
            return
        if amount <= 0:
            Alert().show("Amount must be greater than 0", "warning")
            return
        if self.is_fiat:
            if not self.app.price or self.app.price <= 0:
                Alert().show("Price unavailable", "danger")
                return
            amount_btcz = amount / self.app.price
        else:
            amount_btcz = amount
        amount_sat = int(round(amount_btcz * 1e8))
        if not fee:
            fee_sat = 1000
        else:
            try:
                fee_sat = int(float(fee) * 1e8)
            except ValueError:
                Alert().show("Invalid fee format", "danger")
                return
        total = amount_sat + fee_sat
        if total > self.app.balance:
            Alert().show("Insufficient balance", "danger")
            return
        self.broadcast_drawer = Broadcast(destination, amount_sat, fee_sat)
        self.broadcast_drawer.on_after_hide = self.on_broadcast_hide
        self.broadcast_drawer.confirm_button._impl.native.onclick = self.on_boadcast_click
        self.broadcast_drawer.show()

    
    def on_broadcast_hide(self, event):
        self.broadcast_drawer = None
        

    async def mktx(self):
        from btczpy.transaction import Transaction
        from btczpy.crypto import TYPE_ADDRESS

        SAT_PER_BYTE = 1
        DUST_LIMIT = 546

        utxos = await self.app.client.get_listunspent(self.app.wallet.address)
        if not utxos:
            Alert().show("No available UTXOs", "danger")
            return
        
        amount = self.broadcast_drawer.amount
        utxos.sort(key=lambda x: x["value"])

        selected_utxos = []
        total_input = 0
        manual_fee = 0

        if self.manual_fee:
            try:
                manual_fee = int(
                    float(self.fee_input.value.strip()) * 1e8
                )
            except ValueError:
                Alert().show("Invalid fee format", "danger")
                return

        for utxo in utxos:
            selected_utxos.append(utxo)
            total_input += utxo["value"]

            if self.manual_fee:
                fee = manual_fee
            else:
                fee = (
                    (len(selected_utxos) * 148) +
                    (2 * 34) +
                    10
                ) * SAT_PER_BYTE

            if total_input >= amount + fee:
                break

        if self.manual_fee:
            fee = manual_fee
        else:
            fee = (
                (len(selected_utxos) * 148) +
                (2 * 34) +
                10
            ) * SAT_PER_BYTE

        if total_input < amount + fee:
            Alert().show("Not enough balance", "danger")
            return

        amount = min(amount, total_input - fee)

        inputs = [
            {
                "type": "p2pkh",
                "address": self.app.wallet.address,
                "prevout_hash": u["tx_hash"],
                "prevout_n": u["tx_pos"],
                "value": u["value"],
                "x_pubkeys": [None],
                "pubkeys": [None],
                "signatures": [None],
                "num_sig": 1,
            }
            for u in selected_utxos
        ]
        outputs = [(TYPE_ADDRESS, self.broadcast_drawer.destination, amount)]

        change = total_input - amount - fee

        if 0 < change < DUST_LIMIT:
            fee += change
            change = 0

        if change >= DUST_LIMIT:
            outputs.append((
                TYPE_ADDRESS,
                self.app.wallet.address,
                change
            ))

        tx = Transaction.from_io(inputs, outputs)
        if self.app.wallet.is_unlocked():
            signed_tx = self.sign_transaction(tx)
            if not signed_tx:
                Alert().show("Signing tx failed", "danger")
                return
            self.app.loop.create_task(self.broadcast_tx(signed_tx))
            return

        self.password_dialog = Password(name=self.app.wallet.name)
        self.password_dialog.confirm_button._impl.native.onclick = lambda event, tx=tx: self.on_confirm_broadcast(tx)
        self.password_dialog.cancel_button._impl.native.onclick = self.on_cancel_broadcast
        self.password_dialog.show()


    async def broadcast_tx(self, tx):
        if tx:
            try:
                await self.app.client.broadcast(tx.serialize())
                self.broadcast_drawer.show_success()
                txid = tx.txid()
                self.broadcast_drawer.view_button._impl.native.onclick = lambda event, txid=txid: self.on_view_tx_click(txid)
                self.manual_fee = True
            except Exception:
                Alert().show("Broadcast tx failed", "danger")

            self.clean_inputs()


    def on_confirm_broadcast(self, tx):
        password = self.password_dialog.password_input.value.strip()
        if not password:
            return
        signed_tx = self.sign_transaction(tx, password)
        if not signed_tx:
            Alert().show("Signing tx failed", "danger")
            return
        self.app.loop.create_task(self.broadcast_tx(signed_tx))
        timer = self.password_dialog.timer_slider.value
        if timer > 0:
            self.app.wallet.cache_password(password, timer)
        self.password_dialog.hide()
        self.password_dialog = None


    def sign_transaction(self, tx, password=None):
        try:
            return self.app.wallet.sign_transaction(tx, password)
        except Exception:
            return None
            

    def on_cancel_broadcast(self, event):
        self.password_dialog.hide()
        self.password_dialog = None
            

    def on_boadcast_click(self, event):
        self.app.loop.create_task(self.mktx())


    def on_view_tx_click(self, txid):
        self.broadcast_drawer.hide()
        self.app.loop.create_task(self.get_tx_info(txid))


    async def get_tx_info(self, txid):
        result = await self.app.client.get_transaction(txid)
        if not result:
            Alert().show("Failed to load transaction details", "danger")
            return
        tx = normalize_tx(result, self.app.wallet.address)
        self.tx_drawer = TXInfo(self.app, tx)
        self.tx_drawer.on_after_hide = self.on_hide_txinfo
        self.tx_drawer.show()

    def on_hide_txinfo(self, event):
        self.tx_drawer = None

    def on_resize(self, value):
        if value == "mobile":
            self.send_button_box._impl.native.classList.add("mobile")
        elif value == "desktop":
            self.send_button_box._impl.native.classList.remove("mobile")