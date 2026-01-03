from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers import user, spotify


async def setup_bot() -> tuple[Dispatcher, Bot]:
    """
    Инициализация бота и диспетчера с подключением роутеров.

    :return: Кортеж (Dispatcher, Bot)
    :rtype: tuple[Dispatcher, Bot]
    """
    # Инициализация базы данных
    await init_db()

    # Создание объекта бота
    bot = Bot(token=BOT_TOKEN)

    # Создание диспетчера
    dp = Dispatcher()

    # Подключение роутеров обработчиков
    dp.include_routers(
        user.router,
        spotify.router,
    )

    return dp, bot
