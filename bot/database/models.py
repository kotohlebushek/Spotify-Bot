from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)
    spotify_access_token = fields.TextField(null=True)
    spotify_refresh_token = fields.TextField(null=True)

    class Meta:
        table = "users"
