class TelegramMessageSender:
    def __init__(self, telegram_token):
        self.telegram_token = telegram_token

    def send_add_subscription_success(self):
        ...

    def send_add_subscription_format_error(self):
        ...

    def send_add_subscription_instrument_error(self):
        ...

    def send_delete_subscription_success(self):
        ...

    def send_delete_subscription_not_found_error(self):
        ...

    def send_subscriptions_info(self):
        ...

    def send_notification(self):
        ...

    def send_help(self):
        ...


