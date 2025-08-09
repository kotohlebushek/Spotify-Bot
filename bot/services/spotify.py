import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bot.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SOCKS5_PROXY
from bot.database.models import User  # Модель пользователя
from tortoise.transactions import in_transaction

oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-library-read user-library-modify user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative",
    proxies={"http": SOCKS5_PROXY, "https": SOCKS5_PROXY}
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


async def refresh_user_token(user: User):
    """Обновляет access_token пользователя через refresh_token"""
    try:
        token_info = oauth.refresh_access_token(user.spotify_refresh_token)
        access_token = token_info["access_token"]

        async with in_transaction():
            user.spotify_access_token = access_token
            # сохраняем, если пришёл новый refresh_token (иногда Spotify присылает его)
            if "refresh_token" in token_info:
                user.spotify_refresh_token = token_info["refresh_token"]
            await user.save()

        return access_token
    except Exception as e:
        print(f"Ошибка обновления токена: {e}")
        return None


async def get_spotify_client(user: User):
    """
    Возвращает Spotipy клиент.
    Если токен истёк — обновляет его.
    """

    # Попробуем проверить работу токена простым запросом
    sp = spotipy.Spotify(auth=user.spotify_access_token, proxies={"http": SOCKS5_PROXY, "https": SOCKS5_PROXY})
    try:
        sp.current_user()  # тестовый запрос
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:  # Unauthorized — токен истёк
            new_token = await refresh_user_token(user)
            if not new_token:
                raise e
            sp = spotipy.Spotify(auth=new_token, proxies={"http": SOCKS5_PROXY, "https": SOCKS5_PROXY})
        else:
            raise e

    return sp


async def search_tracks(user, query):
    sp = await get_spotify_client(user)
    result = sp.search(q=query, type="track", limit=5)

    tracks = []
    for item in result["tracks"]["items"]:
        tracks.append({
            "id": item["id"],
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "spotify_url": item["external_urls"]["spotify"]
        })
    return tracks


async def get_track_info(user, track_id):
    try:
        sp = await get_spotify_client(user)
        track = sp.track(track_id)
        return {
            "id": track["id"],
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "spotify_url": track["external_urls"]["spotify"]
        }
    except Exception as e:
        print(f"Error fetching track info: {e}")
        return None


async def play_track(user, track_id):
    try:
        sp = await get_spotify_client(user)

        devices = sp.devices()
        if not devices["devices"]:
            return False, "❌ Нет активного устройства Spotify."

        # Получим ID первого активного устройства (или можно сделать выбор вручную позже)
        device_id = devices["devices"][0]["id"]

        sp.start_playback(
            device_id=device_id,
            uris=[f"spotify:track:{track_id}"]
        )

        return True, "▶️ Воспроизведение началось!"
    except spotipy.exceptions.SpotifyException as e:
        print(f"SpotifyException: {e}")
        return False, "❌ Ошибка при воспроизведении (возможно, нет Premium?)"
    except Exception as e:
        print(f"Error playing track: {e}")
        return False, "❌ Ошибка при воспроизведении."


async def like_track(user, track_id):
    try:
        sp = await get_spotify_client(user)
        sp.current_user_saved_tracks_add([track_id])
        return True
    except Exception as e:
        print(f"Error liking track: {e}")
        return False
