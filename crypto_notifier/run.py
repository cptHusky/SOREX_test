import argparse
import logging
import os

from crypto_notifier import CryptoNotifier, logger


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the crypto notifier bot.")
    parser.add_argument('--log-level',
                        type=str,
                        default='INFO',
                        help='Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--log-path',
                        type=str,
                        default='/var/log/bot.log',
                        help='Path to log file')

    return parser


def configure_logger(log_level, log_path):
    num_log_level = getattr(logging, log_level.upper())
    logging.basicConfig(level=num_log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename=log_path,
                        filemode='a',
                        encoding='utf-8')
    logger.info(f"Logger configured {log_level=}, {log_path=}")


def get_settings():
    env_settings = {
        'telegram_token': os.getenv('TELEGRAM_TOKEN'),
        'coinmarketcap_token': os.getenv('COINMARKETCAP_TOKEN'),
        'coinmarketcap_api_url': os.getenv('COINMARKETCAP_API_URL'),
    }

    class ConfigError(Exception):
        pass

    for setting, value in env_settings.items():
        if value == '':
            logger.info(f"{setting.upper()} is not provided in .env file")
            raise ConfigError(f"{setting.upper()} is not provided in .env file")

    return env_settings


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    configure_logger(args.log_level, args.log_path)
    settings = get_settings()
    app = CryptoNotifier(**settings)
    app.run()
