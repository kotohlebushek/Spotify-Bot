import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
import sys


def setup_logger() -> Logger:
    """
    Настройка логгера для консоли и файла.

    :return: Объект логгера
    :rtype: Logger
    """
    # Создание логгера и установка уровня
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Форматирование логов
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Файловый обработчик с ротацией
    file_handler = RotatingFileHandler(
        "bot.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Инициализация логгера
logger = setup_logger()
