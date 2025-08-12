from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI
import urllib.parse

router = Router()


@router.message(F.text == "/start")
async def start_handler(message: Message):
    """
    Обработчик команды /start — отправляет пользователю ссылку
    для авторизации через Spotify.

    Логика:
        1. Генерируем URL для OAuth авторизации Spotify.
        2. В scope добавляем необходимые права:
           - user-library-read: читать сохранённые треки
           - user-library-modify: добавлять треки в избранное
           - user-read-playback-state: получать состояние плеера
           - user-modify-playback-state: управлять воспроизведением
           - playlist-read-private: читать приватные плейлисты
           - playlist-read-collaborative: читать совместные плейлисты
        3. Передаём telegram_id пользователя в параметр state,
           чтобы связать его после авторизации.
        4. Отправляем inline-кнопку с ссылкой на вход.
    """
    user_id = message.from_user.id

    # Права, которые мы запрашиваем у пользователя
    scope = (
        "user-library-read "
        "user-library-modify "
        "user-read-playback-state "
        "user-modify-playback-state "
        "playlist-read-private "
        "playlist-read-collaborative"
    )

    # Формируем ссылку на авторизацию Spotify
    auth_url = (
            "https://accounts.spotify.com/authorize?"
            + urllib.parse.urlencode({
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scope,
        "state": str(user_id)  # сохраняем telegram_id
    })
    )

    # Клавиатура с кнопкой "Войти через Spotify"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Войти через Spotify", url=auth_url)]
    ])

    # Отправляем приветственное сообщение с кнопкой
    await message.answer(
        "Привет! Чтобы использовать бота, нужно авторизоваться через Spotify:",
        reply_markup=kb
    )
