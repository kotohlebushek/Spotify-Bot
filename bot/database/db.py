from tortoise import Tortoise


async def init_db():
    """
    Инициализация подключения к базе данных с помощью Tortoise ORM.

    Данная функция:
    1. Подключается к базе данных (по умолчанию SQLite, но можно указать PostgreSQL, MySQL и т.д.).
    2. Регистрирует модули с моделями для работы ORM.
    3. Генерирует схемы (CREATE TABLE), если их ещё нет.

    Пример для PostgreSQL:
        await Tortoise.init(
            db_url="postgres://user:password@host:port/database",
            modules={"models": ["bot.database.models"]}
        )

    Примечания:
        - Если база данных ещё не создана, SQLite создаст файл автоматически.
        - Для PostgreSQL/MySQL необходимо создать БД заранее.
    """
    # Шаг 1: Инициализация ORM и подключение к базе
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",  # Для SQLite локальный файл. Можно заменить на PostgreSQL/MySQL.
        modules={"models": ["bot.database.models"]}  # Путь к модулям, где хранятся модели ORM.
    )

    # Шаг 2: Генерация схем на основе моделей (CREATE TABLE, если их нет)
    await Tortoise.generate_schemas()
