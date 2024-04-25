from crypto_notifier import CryptoNotifier


def get_settings():
    return {
        'telegram_token': 'telegram_token',
        'coinmarketcap_token': 'coinmarketcap_token',
        'coinmarketcap_api_url': 'coinmarketcap_api_url',
    }


if __name__ == '__main__':
    settings = get_settings()
    app = CryptoNotifier(**settings)
    app.run()
