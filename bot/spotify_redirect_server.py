from aiohttp import web
from bot.services.spotify import exchange_code_for_token

routes = web.RouteTableDef()


@routes.get("/callback")
async def spotify_callback(request):
    code = request.query.get("code")
    state = request.query.get("state")  # Здесь мы передавали Telegram user_id
    if not code or not state:
        return web.Response(text="Ошибка: отсутствует код или state.")

    # Обмен кода на токен и сохранение в БД
    await exchange_code_for_token(code, int(state))

    return web.Response(text="✅ Авторизация прошла успешно! Можете вернуться в Telegram-бота.")


app = web.Application()
app.add_routes(routes)


def run_server():
    web.run_app(app, port=8888)
