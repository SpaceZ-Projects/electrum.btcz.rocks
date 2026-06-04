
import time
import asyncio
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN
from toga_web.libs import create_element

from .util import normalize_tx
from .transaction import Transaction, TXInfo
from .widget import Alert


class History(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "history_page",
            style=Pack(
                direction=COLUMN,
                flex=1
            )
        )

        self.app = app

        self.history_trigger = False
        self.tx_widgets = {}

        self.tx_drawer = None

        self.spinner = create_element(
            "sl-spinner",
            id="history_spinner"
        )

        self.transactions_box = toga.Box(
            id="history_transactions_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.add(
            self.transactions_box
        )
        self.transactions_box._impl.native.appendChild(
            self.spinner
        )


    def clear_history(self):
        native = self.transactions_box._impl.native
        while native.firstChild:
            native.removeChild(native.firstChild)
        self.tx_widgets.clear()
        self.transactions_box._impl.native.appendChild(
            self.spinner
        )
        self.spinner.classList.remove("hidden")


    async def load_history(self):
        if not self.history_trigger:
            try:
                history = await self.app.client.get_history(self.app.wallet.address)
                mempool = await self.app.client.get_mempool(self.app.wallet.address)
                txids = [tx["tx_hash"] for tx in history + mempool]
                tasks = [self.app.client.get_transaction(txid) for txid in txids]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                valid_txs = [tx for tx in results if isinstance(tx, dict)]
                valid_txs.sort(key=lambda tx: tx.get("time", 0) or time.time(), reverse=False)
                self.spinner.classList.add("hidden")
                for data in valid_txs:
                    txid = data["txid"]
                    if txid in self.tx_widgets:
                        continue
                    tx_widget = Transaction(self.app, data)
                    tx_widget._impl.native.onclick = lambda event, txid=txid: self.on_tx_click(txid)
                    self.transactions_box._impl.native.insertBefore(
                        tx_widget._impl.native,
                        self.transactions_box._impl.native.firstChild
                    )
                    self.tx_widgets[txid] = tx_widget

            except Exception:
                pass
            self.history_trigger = True


    async def update_history(self):
        try:
            history = await self.app.client.get_history(self.app.wallet.address)
            mempool = await self.app.client.get_mempool(self.app.wallet.address)
            txs = history + mempool
            tx_map = {tx["tx_hash"]: tx for tx in txs}
            new_txids = set(tx_map.keys())
            current_txids = set(self.tx_widgets.keys())
            for txid in new_txids - current_txids:
                data = await self.app.client.get_transaction(txid)
                if data:
                    tx_widget = Transaction(self.app, data)
                    tx_widget._impl.native.onclick = lambda event, txid=txid: self.on_tx_click(txid)
                    self.transactions_box._impl.native.insertBefore(
                        tx_widget._impl.native,
                        self.transactions_box._impl.native.firstChild
                    )
                    self.tx_widgets[txid] = tx_widget
                    tx_widget.pulse()

            for txid, widget in self.tx_widgets.items():
                tx = tx_map.get(txid)
                if not tx:
                    continue
                tx_height = tx.get("height")
                if not tx_height:
                    confirmations = 0
                else:
                    confirmations = self.app.height - tx_height + 1
                confirmations = max(confirmations, 0)
                if confirmations <= 4:
                    widget.update_transaction()

        except Exception:
            pass


    async def update_confirmations(self):
        try:
            history = await self.app.client.get_history(self.app.wallet.address)
            tx_map = {tx["tx_hash"]: tx for tx in history}
            for txid, widget in self.tx_widgets.items():
                tx = tx_map.get(txid)
                if not tx:
                    continue
                tx_height = tx.get("height")
                if not tx_height:
                    confirmations = 0
                else:
                    confirmations = self.app.height - tx_height + 1
                confirmations = max(confirmations, 0)
                if confirmations <= 4:
                    widget.update_transaction()
            
            if self.tx_drawer:
                self.tx_drawer.update_info()
        except Exception:
            pass


    def on_tx_click(self, txid):
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