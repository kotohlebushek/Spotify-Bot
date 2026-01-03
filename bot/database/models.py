from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    Модель пользователя для хранения данных Telegram и Spotify.

    :ivar id: Внутренний ID записи
    :ivar telegram_id: ID пользователя Telegram
    :ivar spotify_access_token: Токен доступа Spotify
    :ivar spotify_refresh_token: Токен обновления Spotify
    """
    # Первичный ключ
    id = fields.IntField(pk=True)

    # Telegram ID пользователя (уникальный)
    telegram_id = fields.BigIntField(unique=True)

    # Токен доступа Spotify
    spotify_access_token = fields.TextField(null=True)

    # Токен обновления Spotify
    spotify_refresh_token = fields.TextField(null=True)

    class Meta:
        # Название таблицы в базе
        table = "users"
