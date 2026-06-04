
import toga
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW
from toga_web.libs import create_element


class Menu(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "desktop_menu",
            style=Pack(
                direction=COLUMN
            )
        )

        self.app = app

        electrum_title = create_element(
            "img",
            id="menu_electrum_title",
            src="/static/assets/Title.png"
        )

        electrum_box = toga.Box(
            id="menu_electrum_box",
            style=Pack(
                direction=COLUMN
            )
        )

        history_icon = create_element(
            "sl-icon",
            id="menu_history_icon",
            name="arrow-left-right"
        )

        history_label = toga.Label(
            id="menu_history_label",
            text="Transactions"
        )

        self.history_button = toga.Box(
            id="menu_history_button",
            style=Pack(
                direction=ROW
            )
        )

        receive_icon = create_element(
            "sl-icon",
            id="menu_receive_icon",
            name="download"
        )

        receive_label = toga.Label(
            id="menu_receive_label",
            text="Receive"
        )

        self.receive_button = toga.Box(
            id="menu_receive_button",
            style=Pack(
                direction=ROW
            )
        )

        send_icon = create_element(
            "sl-icon",
            id="menu_send_icon",
            name="send"
        )

        send_label = toga.Label(
            id="menu_send_label",
            text="Send"
        )

        self.send_button = toga.Box(
            id="menu_send_button",
            style=Pack(
                direction=ROW
            )
        )

        tools_icon = create_element(
            "sl-icon",
            id="menu_tools_icon",
            name="tools"
        )

        tools_label = toga.Label(
            id="menu_tools_label",
            text="Tools"
        )

        self.tools_button = toga.Box(
            id="menu_tools_button",
            style=Pack(
                direction=ROW
            )
        )

        settings_icon = create_element(
            "sl-icon",
            id="menu_settings_icon",
            name="gear"
        )

        settings_label = toga.Label(
            id="menu_settings_label",
            text="Settings"
        )

        self.settings_button = toga.Box(
            id="menu_settings_button",
            style=Pack(
                direction=ROW
            )
        )

        navigation_box = toga.Box(
            id="menu_navigation_box",
            style=Pack(
                direction=COLUMN
            )
        )

        self.add(
            electrum_box,
            navigation_box
        )
        electrum_box._impl.native.appendChild(
            electrum_title
        )
        navigation_box.add(
            self.history_button,
            self.receive_button,
            self.send_button,
            self.tools_button,
            self.settings_button
        )
        self.history_button._impl.native.appendChild(
            history_icon
        )
        self.history_button.add(
            history_label
        )
        self.receive_button._impl.native.appendChild(
            receive_icon
        )
        self.receive_button.add(
            receive_label
        )
        self.send_button._impl.native.appendChild(
            send_icon
        )
        self.send_button.add(
            send_label
        )
        self.tools_button._impl.native.appendChild(
            tools_icon
        )
        self.tools_button.add(
            tools_label
        )
        self.settings_button._impl.native.appendChild(
            settings_icon
        )
        self.settings_button.add(
            settings_label
        )



class MobileMenu(toga.Box):
    def __init__(self, app:toga.App):
        super().__init__(
            id= "mobile_menu",
            style=Pack(
                direction=COLUMN
            )
        )

        self.app = app

        history_icon = create_element(
            "sl-icon",
            id="mobile_menu_history_icon",
            name="arrow-left-right"
        )

        history_label = toga.Label(
            id="mobile_menu_history_label",
            text="Transactions"
        )

        self.history_button = toga.Box(
            id="mobile_menu_history_button",
            style=Pack(
                direction=COLUMN
            )
        )

        receive_icon = create_element(
            "sl-icon",
            id="mobile_menu_receive_icon",
            name="download"
        )

        receive_label = toga.Label(
            id="mobile_menu_receive_label",
            text="Receive"
        )

        self.receive_button = toga.Box(
            id="mobile_menu_receive_button",
            style=Pack(
                direction=COLUMN
            )
        )

        send_icon = create_element(
            "sl-icon",
            id="mobile_menu_send_icon",
            name="send"
        )

        send_label = toga.Label(
            id="mobile_menu_send_label",
            text="Send"
        )

        self.send_button = toga.Box(
            id="mobile_menu_send_button",
            style=Pack(
                direction=COLUMN
            )
        )

        tools_icon = create_element(
            "sl-icon",
            id="mobile_menu_tools_icon",
            name="tools"
        )

        tools_label = toga.Label(
            id="mobile_menu_tools_label",
            text="Tools"
        )

        self.tools_button = toga.Box(
            id="mobile_menu_tools_button",
            style=Pack(
                direction=COLUMN
            )
        )

        settings_icon = create_element(
            "sl-icon",
            id="mobile_menu_settings_icon",
            name="gear"
        )

        settings_label = toga.Label(
            id="mobile_menu_settings_label",
            text="Settings"
        )

        self.settings_button = toga.Box(
            id="mobile_menu_settings_button",
            style=Pack(
                direction=COLUMN
            )
        )

        navigation_box = toga.Box(
            id="mobile_menu_navigation_box",
            style=Pack(
                direction=ROW
            )
        )

        self.add(
            navigation_box
        )
        navigation_box.add(
            self.history_button,
            self.receive_button,
            self.send_button,
            self.tools_button,
            self.settings_button
        )
        self.history_button._impl.native.appendChild(
            history_icon
        )
        self.history_button.add(
            history_label
        )
        self.receive_button._impl.native.appendChild(
            receive_icon
        )
        self.receive_button.add(
            receive_label
        )
        self.send_button._impl.native.appendChild(
            send_icon
        )
        self.send_button.add(
            send_label
        )
        self.tools_button._impl.native.appendChild(
            tools_icon
        )
        self.tools_button.add(
            tools_label
        )
        self.settings_button._impl.native.appendChild(
            settings_icon
        )
        self.settings_button.add(
            settings_label
        )