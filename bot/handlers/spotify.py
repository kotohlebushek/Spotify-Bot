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
    Обработка команды поиска трека.

    :param message: Сообщение пользователя
    :type message: Message
    :return: None
    """
    # Получение запроса из текста команды
    query = message.text.replace("/search", "").strip()

    # Проверка на пустой запрос
    if not query:
        await message.answer("🔎 Введите запрос: `/search название трека`", parse_mode="Markdown")
        return

    # Получение пользователя из БД
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user or not user.spotify_access_token:
        await message.answer("⚠️ Сначала авторизуйтесь через /start.")
        return

    # Поиск треков через Spotify
    tracks = await search_tracks(user, query)
    if not tracks:
        await message.answer("❌ Ничего не найдено.")
        return

    # Формирование клавиатуры с найденными треками
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
    Обработка выбора трека из поиска.

    :param callback: CallbackQuery от кнопки
    :type callback: CallbackQuery
    :return: None
    """
    # Извлечение ID трека и запроса
    data = callback.data[len("track_select:"):]
    track_id, query = data.split("|", 1)

    # Проверка авторизации пользователя
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    # Получение информации о треке
    track = await get_track_info(user, track_id)
    if not track:
        await callback.answer("❌ Не удалось получить информацию", show_alert=True)
        return

    # Клавиатура с действиями для трека
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
    Возврат к результатам поиска.

    :param callback: CallbackQuery от кнопки
    :type callback: CallbackQuery
    :return: None
    """
    # Удаление предыдущего сообщения
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith("queue:"))
async def queue_track_handler(callback: CallbackQuery):
    """
    Добавление трека в очередь воспроизведения.

    :param callback: CallbackQuery от кнопки
    :type callback: CallbackQuery
    :return: None
    """
    data = callback.data[len("queue:"):]
    track_id, query = data.split("|", 1)

    # Проверка авторизации
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    from bot.services.spotify import add_track_to_queue
    success, message = await add_track_to_queue(user, track_id)
    # Ответ пользователю с результатом
    await callback.answer(message, show_alert=not success)


@router.callback_query(F.data.startswith("play:"))
async def play_track_handler(callback: CallbackQuery):
    """
    Воспроизведение выбранного трека.

    :param callback: CallbackQuery от кнопки
    :type callback: CallbackQuery
    :return: None
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
    Лайк трека в Spotify.

    :param callback: CallbackQuery от кнопки
    :type callback: CallbackQuery
    :return: None
    """
    data = callback.data[len("like:"):]
    track_id, query = data.split("|", 1)

    # Проверка авторизации
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    # Лайк трека
    success = await like_track(user, track_id)
    if success:
        await callback.answer("❤️ Добавлено в избранное!")
    else:
        await callback.answer("❌ Ошибка при добавлении", show_alert=True)
