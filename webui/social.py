

import toga
from toga.style.pack import Pack
from toga.constants import ROW
from toga_web.libs import create_element


class Social(toga.Box):
    def __init__(self):
        super().__init__(
            id="social_box",
            style=Pack(direction=ROW)
        )

        twitter = self.create_link_icon(
            icon_name="twitter-x",
            url="https://x.com/BTCZOfficial",
            icon_id="social_twitter_icon"
        )

        github = self.create_link_icon(
            icon_name="github",
            url="https://github.com/SpaceZ-Projects/electrum.btcz.rocks",
            icon_id="social_github_icon"
        )

        discord = self.create_link_icon(
            icon_name="discord",
            url="https://discord.com/invite/aAU2WeJ",
            icon_id="social_discord_icon"
        )

        self._impl.native.appendChild(twitter)
        self._impl.native.appendChild(github)
        self._impl.native.appendChild(discord)


    def create_link_icon(self, icon_name, url, icon_id):
        a = create_element(
            "a",
            href=url
        )
        a.target = "_blank"
        a.rel = "noopener noreferrer"
        icon = create_element(
            "sl-icon",
            id=icon_id,
            name=icon_name
        )
        a.appendChild(icon)
        return a