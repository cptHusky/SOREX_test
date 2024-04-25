import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='bot.log',
                    filemode='w',
                    encoding='utf-8')
logger = logging.getLogger(__name__)
