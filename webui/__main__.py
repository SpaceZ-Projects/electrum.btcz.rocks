
import toga
from webui.app import WebUI

class BitcoinZ(toga.App):

    wallet = None
    client = None
    height = 0
    balance = 0
    price = 0

    def startup(self):
        self.main_window = WebUI()


def main():
    app = BitcoinZ(
        formal_name = "BitcoinZ - Electrum Web Wallet",
        app_id = "com.btcz.electrum",
        home_page = "https://electrum.btcz.rocks",
        author = "BTCZCommunity",
        version="1.0.8"
    )
    app.main_loop()

if __name__ == "__main__":
    main()