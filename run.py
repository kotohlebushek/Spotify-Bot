import asyncio
from bot.main import setup_bot
from aiohttp import web
from bot.spotify_redirect_server import app as redirect_app  # aiohttp-приложение для OAuth callback


async def run_bot_and_server():
    """
    Запускает одновременно Telegram-бота и aiohttp сервер для обработки Spotify OAuth.
    """
    # Инициализация бота и диспетчера
    dp, bot = await setup_bot()

    # Запуск aiohttp сервера в фоне (порт 8888)
    runner = web.AppRunner(redirect_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8888)
    await site.start()

    print("✅ Redirect сервер запущен на http://localhost:8888")
    print("🚀 Бот запущен!")

    # Запуск Telegram-бота (long polling)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(run_bot_and_server())
    except (KeyboardInterrupt, SystemExit):
        print("⛔ Бот остановлен.")
