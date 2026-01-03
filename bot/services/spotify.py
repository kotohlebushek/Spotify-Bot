import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from bot.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    SOCKS5_PROXY
)
from bot.database.models import User
from tortoise.transactions import in_transaction
from bot.utils.logger import logger

# Настройка OAuth для Spotify
oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=(
        "user-library-read user-library-modify "
        "user-read-playback-state user-modify-playback-state "
        "playlist-read-private playlist-read-collaborative"
    ),
    proxies={"http": SOCKS5_PROXY, "https": SOCKS5_PROXY}
)


async def exchange_code_for_token(code: str, telegram_id: int):
    """
    Обмен кода авторизации на токен и сохранение в БД.

    :param code: Код авторизации от Spotify
    :type code: str
    :param telegram_id: ID пользователя Telegram
    :type telegram_id: int
    :return: None
    """
    token_info = oauth.get_access_token(code, as_dict=True)
    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]

    # Сохранение токенов в БД
    async with in_transaction():
        user, _ = await User.get_or_create(telegram_id=telegram_id)
        user.spotify_access_token = access_token
        user.spotify_refresh_token = refresh_token
        await user.save()


async def refresh_user_token(user: User) -> str | None:
    """
    Обновление токена Spotify для пользователя.

    :param user: Объект пользователя
    :type user: User
    :return: Новый access_token или None при ошибке
    :rtype: str | None
    """
    try:
        token_info = oauth.refresh_access_token(user.spotify_refresh_token)
        access_token = token_info["access_token"]

        # Обновление токенов в БД
        async with in_transaction():
            user.spotify_access_token = access_token
            if "refresh_token" in token_info:
                user.spotify_refresh_token = token_info["refresh_token"]
            await user.save()

        return access_token
    except Exception as e:
        logger.error(f"Ошибка обновления токена: {e}")
        return None


async def get_spotify_client(user: User) -> Spotify:
    """
    Получение клиента Spotify с проверкой токена.

    :param user: Объект пользователя
    :type user: User
    :return: Объект Spotify
    :rtype: Spotify
    """
    sp = spotipy.Spotify(auth=user.spotify_access_token, proxies={"http": SOCKS5_PROXY, "https": SOCKS5_PROXY})

    # Проверка валидности токена
    try:
        sp.current_user()
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            new_token = await refresh_user_token(user)
            if not new_token:
                raise e
            sp = spotipy.Spotify(auth=new_token, proxies={"http": SOCKS5_PROXY, "https": SOCKS5_PROXY})
        else:
            raise e

    return sp


async def search_tracks(user: User, query: str) -> list[dict]:
    """
    Поиск треков в Spotify.

    :param user: Пользователь
    :type user: User
    :param query: Строка поиска
    :param query: str
    :return: Список словарей с информацией о треках
    :rtype: list[dict]
    """
    sp = await get_spotify_client(user)
    result = sp.search(q=query, type="track", limit=5)

    # Формирование списка треков
    return [
        {
            "id": item["id"],
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "spotify_url": item["external_urls"]["spotify"]
        }
        for item in result["tracks"]["items"]
    ]


async def get_track_info(user: User, track_id: str) -> dict | None:
    """
    Получение информации о треке по ID.

    :param user: Пользователь
    :type user: User
    :param track_id: ID трека
    :type track_id: str
    :return: Словарь с информацией о треке или None
    :rtype: dict | None
    """
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
        logger.info(f"Error fetching track info: {e}")
        return None


async def play_track(user: User, track_id: str) -> tuple[bool, str]:
    """
    Воспроизведение трека на устройстве пользователя.

    :param user: Пользователь
    :type user: User
    :param track_id: ID трека
    :type track_id: str
    :return: Кортеж (успех, сообщение)
    :rtype: tuple[bool, str]
    """
    try:
        sp = await get_spotify_client(user)
        devices = sp.devices()

        # Проверка наличия активного устройства
        if not devices["devices"]:
            return False, "❌ Нет активного устройства Spotify."

        device_id = devices["devices"][0]["id"]
        sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
        return True, "▶️ Воспроизведение началось!"
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"SpotifyException: {e}")
        return False, "❌ Ошибка при воспроизведении (возможно, нет Premium?)"
    except Exception as e:
        logger.error(f"Error playing track: {e}")
        return False, "❌ Ошибка при воспроизведении."


async def like_track(user: User, track_id: str) -> bool:
    """
    Добавление трека в избранное пользователя.

    :param user: Пользователь
    :type user: User
    :param track_id: ID трека
    :type track_id: str
    :return: True при успехе, False при ошибке
    :rtype: bool
    """
    try:
        sp = await get_spotify_client(user)
        sp.current_user_saved_tracks_add([track_id])
        return True
    except Exception as e:
        logger.error(f"Error liking track: {e}")
        return False


async def add_track_to_queue(user: User, track_id: str) -> tuple[bool, str]:
    """
    Добавление трека в очередь воспроизведения.

    :param user: Пользователь
    :type user: User
    :param track_id: ID трека
    :type track_id: str
    :return: Кортеж (успех, сообщение)
    :rtype: tuple[bool, str]
    """
    try:
        sp = await get_spotify_client(user)
        devices = sp.devices()

        if not devices["devices"]:
            return False, "❌ Нет активного устройства Spotify."

        sp.add_to_queue(uri=f"spotify:track:{track_id}")
        return True, "➕ Трек добавлен в очередь!"
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"SpotifyException: {e}")
        return False, "❌ Ошибка при добавлении в очередь (возможно, нет Premium?)"
    except Exception as e:
        logger.error(f"Error adding to queue: {e}")
        return False, "❌ Ошибка при добавлении в очередь."
