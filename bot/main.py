from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers import user, spotify


async def setup_bot() -> Dispatcher:
    # Инициализация БД
    await init_db()

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация всех роутеров
    dp.include_routers(
        user.router,
        spotify.router
    )

    return dp, bot
