from telegram import Update
from telegram.ext import ContextTypes

from logger import logger
from messages import subscription_format_error_text, help_text
from models import SubscriptionInfo


class TelegramMessageSender:
    @staticmethod
    async def send_add_subscription_success(asset: str,
                                            min_threshold: float,
                                            max_threshold: float,
                                            update: Update) -> None:
        message = f"Обновлены пороги для {asset}:"
        if min_threshold is not None:
            formatted_min = f"{min_threshold:.12f}".rstrip('0').rstrip('.') if min_threshold else min_threshold
            message += f" минимум {formatted_min}"
        if max_threshold is not None:
            formatted_max = f"{max_threshold:.12f}".rstrip('0').rstrip('.') if max_threshold else max_threshold
            message += f", максимум {formatted_max}" if min_threshold is not None else f" максимум {formatted_max}"
        await update.message.reply_text(message)
        logger.debug(
            f"TelegramMessageSender sent add subscription success to {update.message.chat_id} :"
            f" {asset} {min_threshold=} {max_threshold=}")

    @staticmethod
    async def send_add_subscription_format_error(update: Update):
        await update.message.reply_text(subscription_format_error_text)
        logger.debug(f"TelegramMessageSender sent add subscription format error to {update.message.chat_id}")

    @staticmethod
    async def send_add_subscription_asset_error(asset: str, update: Update) -> None:
        await update.message.reply_text(f"Криптовалюта {asset} не найдена.")
        logger.debug(f"TelegramMessageSender sent add subscription asset error to {update.message.chat_id}")

    @staticmethod
    async def send_delete_subscription_success(asset: str, update: Update) -> None:
        await update.message.reply_text(f"Подписка на {asset} удалена.")
        logger.debug(f"TelegramMessageSender sent delete subscription success to  {update.message.chat_id}")

    @staticmethod
    async def send_delete_subscription_not_found_error(asset: str, update: Update) -> None:
        await update.message.reply_text(f"Подписка на {asset} не найдена.")
        logger.debug(f"TelegramMessageSender sent delete subscription not found error to {update.message.chat_id}")

    @staticmethod
    async def send_subscriptions_info(subscriptions: list[SubscriptionInfo], update):
        if subscriptions:
            subscription_texts = []
            for subscription in subscriptions:
                formatted_min = f'{subscription.min_threshold}'.rstrip('0').rstrip('.') \
                    if subscription.min_threshold is not None else "не установлен"
                formatted_max = f'{subscription.max_threshold}'.rstrip('0').rstrip('.') \
                    if subscription.max_threshold is not None else "не установлен"
                subscription_texts.append(f"{subscription.asset}: минимум {formatted_min}, максимум {formatted_max}")
            message = "Ваши текущие подписки:\n" + "\n".join(subscription_texts)
        else:
            message = "У вас нет активных подписок."
        await update.message.reply_text(message)
        logger.debug(f"TelegramMessageSender sent subscriptions info for user {update.message.chat_id}")

    @staticmethod
    async def send_notification(chat_id: int,
                                price: float,
                                asset: str,
                                context: ContextTypes.DEFAULT_TYPE,
                                is_up: bool):
        if is_up:
            message = f"Цена {asset} достигла {price} USD!"
        else:
            message = f"Цена {asset} упала до {price} USD!"
        await context.bot.send_message(chat_id=chat_id, text=message)
        logger.debug(f"TelegramMessageSender sent notification: {chat_id=} {asset=} {price=} {is_up=}")

    @staticmethod
    async def send_help(update: Update,
                        prepend: str = '') -> None:
        help_message = prepend + help_text
        await update.message.reply_text(help_message, parse_mode='MarkdownV2')
        logger.debug(f"TelegramMessageSender sent help message: {help_message}")
