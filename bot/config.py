from dotenv import load_dotenv
import os

"""
Загрузка переменных окружения из .env
"""

# Инициализация переменных окружения
load_dotenv()

# Токен Telegram бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Параметры Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Прокси SOCKS5 (опционально)
SOCKS5_PROXY = os.getenv("SOCKS5_PROXY")
