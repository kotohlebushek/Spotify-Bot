from tortoise import Tortoise


async def init_db():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",  # или PostgreSQL
        modules={"models": ["bot.database.models"]}
    )
    await Tortoise.generate_schemas()
