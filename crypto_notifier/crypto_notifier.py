import logging

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from logger import logger
from messages import start_prepend, handle_unknown_prepend
from models import SubscriptionInfo
from telegram_message_sender import TelegramMessageSender


class CoinMarketCapClient:
    def __init__(self, coinmarketcap_api_url: str, coinmarketcap_token: str):
        self.coinmarketcap_token = coinmarketcap_token
        self.coinmarketcap_url = coinmarketcap_api_url
        logger.info(f"CoinMarketCapClient initialized, {coinmarketcap_api_url=}")

    def get_prices(self, assets: list | str) -> dict:
        symbol = ','.join(assets) if isinstance(assets, list) else assets
        params = {
            'symbol': symbol,
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.coinmarketcap_token,
        }
        logger.info(f"CoinMarketCapClient requested {assets}")
        response = requests.get(self.coinmarketcap_url, headers=headers, params=params)
        logger.debug(f"CoinMarketCapClient sent: headers={headers}, params={params}")
        data = response.json()
        logger.debug(f"CoinMarketCapClient received: {data}")
        return data['data']


class CryptoNotifier:
    def __init__(self,
                 coinmarketcap_api_url: str,
                 coinmarketcap_token: str,
                 telegram_token: str,
                 log_level: str,
                 log_path):
        num_log_level = getattr(logging, log_level.upper())
        logging.basicConfig(level=num_log_level,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            filename=log_path,
                            filemode='a',
                            encoding='utf-8')
        logger.info(f"CryptoNotifier initializing, {log_level=}, {log_path=}")

        self.telegram_token = telegram_token
        self.client = CoinMarketCapClient(coinmarketcap_api_url, coinmarketcap_token)
        self.sender = TelegramMessageSender()
        self.watchlist = {}  # {'asset': {'chat_id': (min_threshold, max_threshold)}}

        logger.info(f"CryptoNotifier initialized")

    async def process_subscription_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        try:
            asset = context.args[0].upper()
            raw_min_threshold = float(context.args[1])
            raw_max_threshold = float(context.args[2])

            if raw_min_threshold == 0 and raw_max_threshold == 0:
                await self.delete_subscription(asset, chat_id, update)
                return
            if not self._check_asset_exists(asset):
                logger.info(f"CryptoNotifier received subscription for invalid asset {asset} from {chat_id}")
                await self.sender.send_add_subscription_asset_error(asset, update)
                return
            min_threshold = None if raw_min_threshold == 0 else round(raw_min_threshold, 12)
            max_threshold = None if raw_max_threshold == 0 else round(raw_max_threshold, 12)

            self._add_subscription(asset, chat_id, min_threshold, max_threshold)

            await self.sender.send_add_subscription_success(asset, min_threshold, max_threshold, update)
        except (IndexError, ValueError):
            logger.warning(f"CryptoNotifier failed to set thresholds for user {chat_id} with input: {context.args}")
            await self.sender.send_add_subscription_format_error(update)

    def _add_subscription(self,
                          asset: str,
                          chat_id: int,
                          min_threshold: float,
                          max_threshold: float) -> None:
        if self.watchlist.get(asset) is None:
            self.watchlist[asset] = {chat_id: (min_threshold, max_threshold)}
        self.watchlist[asset] |= {chat_id: (min_threshold, max_threshold)}
        logger.info(f"CryptoNotifier added subscription for user {chat_id}: {asset} {min_threshold=} {max_threshold=}")
        logger.debug(f"CryptoNotifier current {self.watchlist=}")

    async def delete_subscription(self, asset: str, chat_id: int, update: Update) -> None:
        if asset in self.watchlist and chat_id in self.watchlist[asset]:
            del self.watchlist[asset][chat_id]
            if not self.watchlist[asset]:
                del self.watchlist[asset]
            logger.info(f"CryptoNotifier deleted subscription for user {chat_id} : {asset}")
            await self.sender.send_delete_subscription_success(asset, update)
            logger.debug(f"CryptoNotifier current {self.watchlist=}")
        else:
            await self.sender.send_delete_subscription_not_found_error(asset, update)

    async def show_subscriptions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        subscriptions = []
        for asset, chats in self.watchlist.items():
            if chat_id in chats:
                min_threshold, max_threshold = chats[chat_id]
                subscription = SubscriptionInfo(asset, min_threshold, max_threshold)
                subscriptions.append(subscription)
        logger.info(f"CryptoNotifier found {len(subscriptions)} subscriptions "
                    f"for user {update.message.chat_id} : {subscriptions}")
        await self.sender.send_subscriptions_info(subscriptions, update)

    async def check_prices(self, context: ContextTypes.DEFAULT_TYPE):
        if self.watchlist:
            asset_list = list(self.watchlist.keys())
            logger.debug(f"CryptoNotifier requesting prices for assets: {asset_list}")
            prices = self.client.get_prices(asset_list)
            logger.debug(f"CryptoNotifier received prices")
            for asset, chats in self.watchlist.items():
                price = round(prices[asset]['quote']['USD']['price'], 12)
                logger.debug(f"CryptoNotifier currently processing {asset} : {price}")
                for chat_id, thresholds in chats.items():
                    min_threshold, max_threshold = thresholds
                    is_up = None
                    if max_threshold and price >= max_threshold:
                        is_up = True
                    elif min_threshold and price <= min_threshold:
                        is_up = False
                    if is_up is not None:
                        await self.sender.send_notification(chat_id, price, asset, context, is_up)
                        logger.info(f"CryptoNotifier sent notification to user {chat_id} about {asset}")
                        logger.debug(f"{price=} {is_up=} threshold={max_threshold if is_up else min_threshold}")

    def _check_asset_exists(self, asset: str) -> bool:
        data = self.client.get_prices(asset)
        return data != {}

    async def start_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.debug(f"CryptoNotifier received /start message from {update.message.chat_id}, responding:")
        await self.sender.send_help(update=update, prepend=start_prepend)

    async def help_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.debug(f"CryptoNotifier received /help message from {update.message.chat_id}, responding:")
        await self.sender.send_help(update=update)

    async def handle_unknown_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.debug(f"CryptoNotifier received unknown message from {update.message.chat_id}, responding:")
        await self.sender.send_help(update=update, prepend=handle_unknown_prepend)

    def run(self) -> None:
        application = Application.builder().token(self.telegram_token).build()
        application.add_handler(CommandHandler('start', self.start_message))
        application.add_handler(CommandHandler('subscribe', self.process_subscription_action))
        application.add_handler(CommandHandler('subscriptions', self.show_subscriptions))
        application.add_handler(CommandHandler('help', self.help_message))
        application.add_handler(MessageHandler(filters.COMMAND, self.handle_unknown_message))
        application.add_handler(MessageHandler(filters.TEXT, self.handle_unknown_message))
        j = application.job_queue
        j.run_repeating(self.check_prices, interval=10, first=0)
        application.run_polling()
