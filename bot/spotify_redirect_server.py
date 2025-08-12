from aiohttp import web
from bot.services.spotify import exchange_code_for_token

routes = web.RouteTableDef()


@routes.get("/callback")
async def spotify_callback(request):
    """
    Обработчик для редиректа Spotify OAuth.
    Получает code и state (Telegram user_id),
    обменивает code на токены и сохраняет их.
    """
    code = request.query.get("code")
    state = request.query.get("state")  # Telegram user_id

    if not code or not state:
        return web.Response(text="Ошибка: отсутствует code или state.")

    # Сохраняем токены в БД
    await exchange_code_for_token(code, int(state))

    return web.Response(text="✅ Авторизация прошла успешно! Можете вернуться в Telegram-бота.")


app = web.Application()
app.add_routes(routes)


def run_server():
    """
    Запускает aiohttp сервер на порту 8888.
    """
    web.run_app(app, port=8888)
