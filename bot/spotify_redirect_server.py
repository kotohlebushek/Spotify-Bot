from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from bot.services.spotify import exchange_code_for_token

"""
Сервер для обработки колбэка Spotify OAuth
"""

# Таблица маршрутов
routes = web.RouteTableDef()


@routes.get("/callback")
async def spotify_callback(request: Request) -> Response:
    """
    Обработка колбэка Spotify после авторизации.

    :param request: HTTP-запрос
    :type request: Request
    :return: HTTP-ответ с результатом авторизации
    :rtype: Response
    """
    # Получение кода и состояния из запроса
    code = request.query.get("code")
    state = request.query.get("state")

    # Проверка наличия обязательных параметров
    if not code or not state:
        return web.Response(text="Ошибка: отсутствует code или state.")

    # Обмен кода на токен
    await exchange_code_for_token(code, int(state))

    return web.Response(text="✅ Авторизация прошла успешно! Можете вернуться в Telegram-бота.")


# Создание приложения и регистрация маршрутов
app = web.Application()
app.add_routes(routes)


def run_server():
    """
    Запуск веб-сервера на порту 8888.
    """
    web.run_app(app, port=8888)
