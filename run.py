import asyncio
from bot.main import setup_bot
from aiohttp import web
from bot.spotify_redirect_server import app as redirect_app  # Импорт aiohttp-сервера


async def run_bot_and_server():
    dp, bot = await setup_bot()

    # Запуск aiohttp-сервера на фоне
    runner = web.AppRunner(redirect_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8888)
    await site.start()

    print("✅ Redirect сервер запущен на http://localhost:8888")
    print("🚀 Бот запущен!")

    # Запуск бота (long polling)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(run_bot_and_server())
    except (KeyboardInterrupt, SystemExit):
        print("⛔ Бот остановлен.")
