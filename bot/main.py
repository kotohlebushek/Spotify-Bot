from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers import user, spotify


async def setup_bot() -> tuple[Dispatcher, Bot]:
    """
    Инициализация базы данных, бота и диспетчера.
    Регистрирует все необходимые роутеры.

    Возвращает кортеж (Dispatcher, Bot).
    """
    # Инициализируем базу данных
    await init_db()

    # Создаем экземпляр бота
    bot = Bot(token=BOT_TOKEN)

    # Создаем диспетчер
    dp = Dispatcher()

    # Регистрируем обработчики (роутеры)
    dp.include_routers(
        user.router,
        spotify.router,
    )

    return dp, bot
