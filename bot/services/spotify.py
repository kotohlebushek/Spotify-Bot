from spotipy.oauth2 import SpotifyOAuth
from bot.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
from bot.database.models import User  # Модель пользователя
from tortoise.transactions import in_transaction

oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-library-read user-library-modify user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative"
)


async def exchange_code_for_token(code: str, telegram_id: int):
    token_info = oauth.get_access_token(code, as_dict=True)
    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]

    async with in_transaction():
        user, _ = await User.get_or_create(telegram_id=telegram_id)
        user.spotify_access_token = access_token
        user.spotify_refresh_token = refresh_token
        await user.save()
