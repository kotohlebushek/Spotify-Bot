from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    Модель пользователя Telegram, связанного с аккаунтом Spotify.

    Поля:
        id (int): Первичный ключ (генерируется автоматически).
        telegram_id (int): Уникальный ID пользователя Telegram (используется для идентификации).
        spotify_access_token (str | None): Access token для Spotify API (живёт ~1 час).
        spotify_refresh_token (str | None): Refresh token для обновления access token'а.

    Примечания:
        - Access token используется для выполнения запросов от имени пользователя.
        - Refresh token не истекает (обычно) и нужен для обновления access token.
        - Если пользователь ещё не авторизовался через Spotify, токены будут равны None.
    """

    # Первичный ключ в базе данных
    id = fields.IntField(pk=True)

    # Уникальный ID пользователя в Telegram
    telegram_id = fields.BigIntField(unique=True)

    # Access token для работы с API Spotify (истекает через 3600 сек)
    spotify_access_token = fields.TextField(null=True)

    # Refresh token для продления access token
    spotify_refresh_token = fields.TextField(null=True)

    class Meta:
        table = "users"  # Явное указание имени таблицы в БД
