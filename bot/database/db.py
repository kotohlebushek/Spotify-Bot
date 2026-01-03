from tortoise import Tortoise


async def init_db():
    """
    Инициализация базы данных и генерация схем.

    :return: None
    """
    # Подключение к базе данных SQLite и регистрация моделей
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["bot.database.models"]}
    )

    # Создание таблиц согласно моделям
    await Tortoise.generate_schemas()
