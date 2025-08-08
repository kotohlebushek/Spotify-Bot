from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI
import urllib.parse

router = Router()


@router.message(F.text == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id
    scope = "user-library-read user-library-modify user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative"

    auth_url = (
            "https://accounts.spotify.com/authorize?"
            + urllib.parse.urlencode({
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scope,
        "state": str(user_id)
    })
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Войти через Spotify", url=auth_url)]
    ])

    await message.answer("Привет! Чтобы использовать бота, нужно авторизоваться через Spotify:", reply_markup=kb)
