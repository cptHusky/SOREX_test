import argparse
import os

from crypto_notifier import CryptoNotifier


def get_settings():
    return {
        'telegram_token': os.getenv('TELEGRAM_TOKEN'),
        'coinmarketcap_token': os.getenv('COINMARKETCAP_TOKEN'),
        'coinmarketcap_api_url': os.getenv('COINMARKETCAP_API_URL'),
    }


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the crypto notifier bot.")
    parser.add_argument('--log-level',
                        type=str,
                        default='INFO',
                        help='Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--log-path',
                        type=str,
                        default='bot.log',
                        help='Path to log file')

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    settings = get_settings() | args.__dict__
    app = CryptoNotifier(**settings)
    app.run()
