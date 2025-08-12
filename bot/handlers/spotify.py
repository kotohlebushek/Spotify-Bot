from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from bot.database.models import User
from bot.services.spotify import (
    like_track,
    search_tracks,
    get_track_info,
)

router = Router()


@router.message(F.text.startswith("/search"))
async def search_command(message: Message):
    """
    Обработчик команды /search — выполняет поиск треков в Spotify.

    Шаги:
        1. Получаем запрос пользователя (всё, что идёт после /search).
        2. Проверяем, авторизован ли пользователь в Spotify.
        3. Делаем запрос к API Spotify на поиск треков.
        4. Если треки найдены — выводим inline-клавиатуру с результатами.
           Каждая кнопка = исполнитель + название трека.
    """
    # Убираем "/search" и лишние пробелы
    query = message.text.replace("/search", "").strip()

    if not query:
        await message.answer("🔎 Введите запрос: `/search название трека`", parse_mode="Markdown")
        return

    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user or not user.spotify_access_token:
        await message.answer("⚠️ Сначала авторизуйтесь через /start.")
        return

    tracks = await search_tracks(user, query)
    if not tracks:
        await message.answer("❌ Ничего не найдено.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{track['artist']} — {track['name']}",
                callback_data=f"track_select:{track['id']}|{query}"
            )
        ] for track in tracks
    ])

    await message.answer("🔍 Найденные треки:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("track_select:"))
async def track_select_handler(callback: CallbackQuery):
    """
    Обработчик выбора трека из списка найденных.

    Шаги:
        1. Получаем ID трека из callback_data.
        2. Проверяем авторизацию пользователя.
        3. Получаем подробную информацию о треке.
        4. Выводим inline-клавиатуру с кнопками:
           ▶️ Воспроизвести
           ❤️ Лайкнуть
           ➕ В очередь
    """
    data = callback.data[len("track_select:"):]
    track_id, query = data.split("|", 1)

    user = await User.get_or_none(telegram_id=callback.from_user.id)
    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    track = await get_track_info(user, track_id)
    if not track:
        await callback.answer("❌ Не удалось получить информацию", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Воспроизвести", callback_data=f"play:{track_id}|{query}")],
        [InlineKeyboardButton(text="❤️ Лайкнуть", callback_data=f"like:{track_id}|{query}")],
        [InlineKeyboardButton(text="➕ В очередь", callback_data=f"queue:{track_id}|{query}")],
        [InlineKeyboardButton(text="⬅️ Назад к результатам поиска", callback_data=f"search_back:{query}")]
    ])

    await callback.message.answer(
        f"*{track['name']}* — {track['artist']}",
        parse_mode="Markdown",
        reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("search_back:"))
async def search_back_handler(callback: CallbackQuery):
    """
    Возвращение к результатам поиска
    """
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith("queue:"))
async def queue_track_handler(callback: CallbackQuery):
    """
    Добавление трека в очередь воспроизведения Spotify.
    """
    data = callback.data[len("queue:"):]
    track_id, query = data.split("|", 1)

    user = await User.get_or_none(telegram_id=callback.from_user.id)
    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    from bot.services.spotify import add_track_to_queue
    success, message = await add_track_to_queue(user, track_id)
    await callback.answer(message, show_alert=not success)


@router.callback_query(F.data.startswith("play:"))
async def play_track_handler(callback: CallbackQuery):
    """
    Воспроизведение выбранного трека на активном устройстве пользователя.
    """
    data = callback.data[len("play:"):]
    track_id, query = data.split("|", 1)

    user = await User.get_or_none(telegram_id=callback.from_user.id)
    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    from bot.services.spotify import play_track
    success, message = await play_track(user, track_id)
    await callback.answer(message, show_alert=not success)


@router.callback_query(F.data.startswith("like:"))
async def like_track_handler(callback: CallbackQuery):
    """
    Добавление трека в избранное пользователя (Liked Songs).
    """
    data = callback.data[len("like:"):]
    track_id, query = data.split("|", 1)

    user = await User.get_or_none(telegram_id=callback.from_user.id)
    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    success = await like_track(user, track_id)
    if success:
        await callback.answer("❤️ Добавлено в избранное!")
    else:
        await callback.answer("❌ Ошибка при добавлении", show_alert=True)
