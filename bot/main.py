from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers import user


async def setup_bot() -> Dispatcher:
    # Инициализация БД
    await init_db()

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация всех роутеров
    dp.include_routers(
        user.router,
    )

    return dp, bot
