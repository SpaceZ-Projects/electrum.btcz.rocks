
import asyncio
import toga
from toga.constants import COLUMN, ROW
from toga.style.pack import Pack
from toga_web.libs import create_element
from js import window, ResizeObserver
from pyodide.ffi import create_proxy

from btczpy.client import ElectrumClient

from .menu import Menu, MobileMenu
from .account import Accounts
from .header import Header
from .history import History
from .receive import Receive
from .send import Send
from .tools import Tools
from .settings import Settings
from .util import get_market


class WebUI(toga.Window):
    def __init__(self):
        super().__init__()

        current_path = window.location.pathname
        parts = current_path.strip("/").split("/")
        if parts or parts != [""]:
            window.history.replaceState(None, "", "/")

        self.active_page = None
        self.menu_active = False
        self.header_active = False

        self.accounts_trigger = True

        self.history_trigger = False
        self.receive_trigger = False
        self.send_trigger = False
        self.tools_trigger = False
        self.settings_trigger = False

        self.headers_subscription = False
        self.current_subscription = None

        self.app.client = ElectrumClient()

        self.menu = Menu(self.app)
        self.mobile_menu = MobileMenu(self.app)
        self.accounts_page = Accounts(self.app)
        self.page_header = Header(self.app)
        self.history_page = History(self.app)
        self.receive_page = Receive(self.app)
        self.send_page = Send(self.app)
        self.tools_page = Tools(self.app)
        self.settings_page = Settings(self.app)

        self.pages = toga.Box(
            id="pages",
            style=Pack(
                direction=COLUMN,
                flex=1
            )
        )

        pwa_button_icon = create_element(
            "sl-icon",
            id="pwa_button_icon",
            name="puzzle"
        )

        pwa_button_label = toga.Label(
            id="pwa_button_label",
            text="Install"
        )

        self.pwa_button = toga.Box(
            id="pwa_button"
        )
        self.pwa_button._impl.native.onclick = self.install_pwa

        pwa_label = toga.Label(
            id="pwa_label",
            text="Electrum Web Wallet"
        )

        self.pwa_box = toga.Box(
            id="pwa_box",
            style=Pack(
                direction=ROW
            )
        )

        self.main_box = toga.Box(
            id="main_box",
            style=Pack(
                direction=ROW,
                flex=1
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.menu,
            self.pages,
            self.pwa_box
        )

        self.pages.add(
            self.page_header,
            self.accounts_page,
            self.history_page,
            self.receive_page,
            self.send_page,
            self.tools_page,
            self.settings_page,
            self.mobile_menu,
        )
        self.pwa_box.add(
            self.pwa_button,
            pwa_label
        )
        self.pwa_button._impl.native.appendChild(
            pwa_button_icon
        )
        self.pwa_button.add(
            pwa_button_label
        )

        self.set_resize_listener()
        self.verify_accounts()
        self.set_navigation_listeners()

    def verify_accounts(self):
        self.set_active(self.accounts_page)
        self.accounts_page.verify_accounts()
        self.app.loop.create_task(self.subscribe_events())
        if not window.isPWAInstalled():
            self.pwa_box._impl.native.classList.add("show")


    def logout_account(self):
        self.accounts_trigger = True
        self.menu_active = False
        self.history_page.history_trigger = False
        self.hide_menu()
        self.page_header._impl.native.classList.remove("active")
        self.header_active = False
        self.unsubscribe_address()
        self.history_page.clear_history()
        self.set_active(self.accounts_page)
        self.accounts_page.reload_accounts()


    def show_wallet(self):
        self.pwa_box._impl.native.classList.remove("show")
        self.accounts_trigger = False
        self.menu_active = True
        self.page_header._impl.native.classList.add("active")
        self.header_active = True
        self._on_resize_window(None, None)
        self.set_active(self.history_page, self.menu.history_button, self.mobile_menu.history_button)
        self.history_trigger = True
        self.page_header.account_name.text = self.app.wallet.name
        self.app.loop.create_task(self.subscribe_address())
        self.app.loop.create_task(self.page_header.update_balance())
        self.app.loop.create_task(self.history_page.load_history())
        self.receive_page.show_qr_code()


    async def pages_transition(self, active_pg, desktop_btn = None, mobile_btn = None):
        buttons = [
            self.menu.history_button,
            self.mobile_menu.history_button,
            self.menu.receive_button,
            self.mobile_menu.receive_button,
            self.menu.send_button,
            self.mobile_menu.send_button,
            self.menu.tools_button,
            self.mobile_menu.tools_button,
            self.menu.settings_button,
            self.mobile_menu.settings_button
        ]
        for btn in buttons:
            btn._impl.native.classList.remove("active")
        if self.active_page:
            self.active_page._impl.native.classList.remove("active")
            await asyncio.sleep(0.2)
            self.active_page._impl.native.classList.remove("show")
        active_pg._impl.native.classList.add('show')
        if desktop_btn:
            desktop_btn._impl.native.classList.add("active")
        if mobile_btn:
            mobile_btn._impl.native.classList.add("active")
        await asyncio.sleep(0.2)
        active_pg._impl.native.classList.add('active')
        self.active_page = active_pg


    def set_active(self, active_pg, active_btn = None, mobile_btn = None):
        self.history_trigger = False
        self.receive_trigger = False
        self.send_trigger = False
        self.tools_trigger = False
        self.settings_trigger = False
        self.app.loop.create_task(self.pages_transition(active_pg, active_btn, mobile_btn))


    def set_resize_listener(self):
        self._resize_listener = create_proxy(self._on_resize_window)
        self._resize_observer = ResizeObserver.new(self._resize_listener)
        self._resize_observer.observe(self.main_box._impl.native)

    
    def _on_resize_window(self, entries, observer):
        width = self.main_box._impl.native.offsetWidth
        if width < 880:
            self.mobile_view()
        else:
            self.desktop_view()


    def set_navigation_listeners(self):
        self.menu.history_button._impl.native.onclick = self.show_history_page
        self.mobile_menu.history_button._impl.native.onclick = self.show_history_page
        self.menu.receive_button._impl.native.onclick = self.show_receive_page
        self.mobile_menu.receive_button._impl.native.onclick = self.show_receive_page
        self.menu.send_button._impl.native.onclick = self.show_send_page
        self.mobile_menu.send_button._impl.native.onclick = self.show_send_page
        self.menu.tools_button._impl.native.onclick = self.show_tools_page
        self.mobile_menu.tools_button._impl.native.onclick = self.show_tools_page
        self.menu.settings_button._impl.native.onclick = self.show_settings_page
        self.mobile_menu.settings_button._impl.native.onclick = self.show_settings_page
        

    def show_history_page(self, event):
        if not self.history_trigger:
            self.set_active(self.history_page, self.menu.history_button, self.mobile_menu.history_button)
            self.history_trigger = True

    def show_receive_page(self, event):
        if not self.receive_trigger:
            self.set_active(self.receive_page, self.menu.receive_button, self.mobile_menu.receive_button)
            self.receive_trigger = True

    def show_send_page(self, event):
        if not self.send_trigger:
            self.set_active(self.send_page, self.menu.send_button, self.mobile_menu.send_button)
            self.send_trigger = True

    def show_tools_page(self, event):
        if not self.tools_trigger:
            self.set_active(self.tools_page, self.menu.tools_button, self.mobile_menu.tools_button)
            self.tools_trigger = True

    def show_settings_page(self, event):
        if not self.settings_trigger:
            self.set_active(self.settings_page, self.menu.settings_button, self.mobile_menu.settings_button)
            self.settings_trigger = True

    def mobile_view(self):
        self.main_box._impl.native.classList.add("mobile")
        if self.menu_active:
            self.menu._impl.native.classList.remove("active")
            self.mobile_menu._impl.native.classList.add("active")
            self.page_header._impl.native.classList.add("mobile")
            self.send_page.on_resize("mobile")
            self.tools_page.on_resize("mobile")

    def desktop_view(self):
        self.main_box._impl.native.classList.remove("mobile")
        if self.menu_active:
            self.mobile_menu._impl.native.classList.remove("active")
            self.menu._impl.native.classList.add("active")
            self.page_header._impl.native.classList.remove("mobile")
            self.send_page.on_resize("desktop")
            self.tools_page.on_resize("desktop")

    
    def hide_menu(self):
        self.menu._impl.native.classList.remove("active")
        self.mobile_menu._impl.native.classList.remove("active")


    def on_events(self, message):
        if message.get("method") == "blockchain.headers.subscribe":
            height = message["params"][0]["height"]
            self.app.height = height
            if self.accounts_trigger:
                self.accounts_page.update_height(height)
            self.page_header.update_height(height)
            self.app.loop.create_task(self.history_page.update_confirmations())
        elif message.get("method") == "blockchain.scripthash.subscribe":
            scripthash = message["params"][0]
            if scripthash != self.current_subscription:
                return
            self.app.loop.create_task(self.page_header.update_balance())
            self.app.loop.create_task(self.history_page.update_history())


    async def subscribe_events(self):
        self.app.client.on_notification = self.on_events
        self.app.client.on_status = self.on_status
        await self.app.client.connect()

    def on_status(self, status):
        if status == "connected":
            self.app.loop.create_task(self.subscribe_headers())
        if self.accounts_trigger:
            self.accounts_page.update_status(status)
        self.page_header.update_status(status)


    async def get_version(self):
        try:
            server = await self.app.client.server_version()
            version = server[0]
            protocol = server[1]
            self.accounts_page.update_version(version, protocol)
            self.page_header.update_version(version, protocol)
        except Exception:
            pass


    async def update_price(self):
        while True:
            try:
                market = await get_market()
                price = market["price_usd"]
                self.app.price = price
                self.page_header.update_price(price)
            except Exception:
                pass
            
            await asyncio.sleep(610)


    async def subscribe_headers(self):
        if not self.headers_subscription:
            result = await self.app.client.subscribe_headers()
            if result and "height" in result:
                height = result["height"]
                self.app.height = height
                self.accounts_page.update_height(height)
                self.page_header.update_height(height)
                self.headers_subscription = True

                self.app.loop.create_task(self.get_version())
                self.app.loop.create_task(self.update_price())


    async def subscribe_address(self):
        self.current_subscription = self.app.wallet.scripthash()
        await self.app.client.subscribe_address(self.app.wallet.address)

    def unsubscribe_address(self):
        self.app.wallet.clear()
        self.current_subscription = None


    async def _install_pwa(self):
        result = await window.installPWA()
        if result:
            self.pwa_box._impl.native.classList.remove("show")
            
    
    def install_pwa(self, event):
        self.app.loop.create_task(self._install_pwa())


    def scroll_pages_to_bottom(self):
        element = self.pages._impl.native
        element.scrollTop = element.scrollHeight