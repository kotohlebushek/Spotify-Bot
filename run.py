import asyncio
from bot.main import setup_bot
from aiohttp import web
from bot.spotify_redirect_server import app as redirect_app
from bot.utils.logger import logger


async def run_bot_and_server():
    """
    Запуск Telegram-бота и веб-сервера для Spotify OAuth.

    :return: None
    """
    # Инициализация бота и диспетчера
    dp, bot = await setup_bot()

    # Настройка и запуск веб-сервера для колбэка Spotify
    runner = web.AppRunner(redirect_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8888)
    await site.start()

    logger.info("✅ Redirect сервер запущен на http://localhost:8888")
    logger.info("🚀 Бот запущен!")

    # Запуск polling Telegram-бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(run_bot_and_server())
    except (KeyboardInterrupt, SystemExit):
        logger.info("⛔ Бот остановлен.")
