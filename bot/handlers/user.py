from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI
from bot.database.models import User
import urllib.parse

router = Router()


@router.message(F.text == "/start")
async def start_handler(message: Message):
    """
    Обработчик команды /start — отправляет пользователю ссылку
    для авторизации через Spotify.

    Если пользователь уже авторизован — просто приветствие.
    """

    user_id = message.from_user.id

    # Проверяем в БД, авторизован ли пользователь
    user = await User.get_or_none(telegram_id=user_id)
    if user and user.spotify_access_token:
        await message.answer(f"👋 Привет снова, {message.from_user.full_name}! Ты уже авторизован.")
        return

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


@router.message(F.text == "/help")
async def help_handler(message: Message):
    """
    Выводит информацию о боте и список доступных команд.
    """
    help_text = (
        "🤖 *Spotify Bot* — помощник для управления музыкой прямо из Telegram.\n\n"
        "Доступные команды:\n"
        "• /start — авторизация через Spotify\n"
        "• /search <название> — поиск трека\n"
        "• /help — показать это сообщение\n\n"
        "💡 После поиска трека вы сможете:\n"
        "   ▶️ Запустить воспроизведение\n"
        "   ❤️ Добавить в избранное\n"
        "   ➕ Добавить в очередь"
    )

    await message.answer(help_text, parse_mode="Markdown")
