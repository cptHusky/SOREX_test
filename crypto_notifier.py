from telegram.ext import Application, CommandHandler, MessageHandler, filters

from telegram_message_sender import TelegramMessageSender


class CoinMarketCapClient:
    def __init__(self, coinmarketcap_api_url: str, coinmarketcap_token: str):
        self.coinmarketcap_token = coinmarketcap_token
        self.coinmarketcap_url = coinmarketcap_api_url

    def get_prices(self, assets: list) -> dict:
        ...


class CryptoNotifier:
    def __init__(self, coinmarketcap_api_url: str, coinmarketcap_token: str, telegram_token: str):
        self.telegram_token = telegram_token
        self.client = CoinMarketCapClient(coinmarketcap_api_url, coinmarketcap_token)
        self.sender = TelegramMessageSender(telegram_token)
        self.watchlist = {}  # {'currency_symbol': {'chat_id': (min_threshold, max_threshold)}}

    def process_subscription_action(self, message):
        ...

    def add_subscription(self, currency: str, chat_id: str, min_threshold: float, max_threshold: float):
        ...

    def delete_subscription(self, currency: str, chat_id: str):
        ...

    def show_subscriptions(self, message):
        ...

    def check_prices(self, bot):
        ...

    def start(self):
        ...

    def help(self):
        ...

    def handle_unknown(self):
        ...

    def run(self):
        application = Application.builder().token(self.telegram_token).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("subscribe", self.process_subscription_action))
        application.add_handler(CommandHandler("subscriptions", self.show_subscriptions))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(MessageHandler(filters.COMMAND, self.handle_unknown))
        application.add_handler(MessageHandler(filters.TEXT, self.handle_unknown))
        j = application.job_queue
        j.run_repeating(self.check_prices, interval=10, first=0)
        application.run_polling()
