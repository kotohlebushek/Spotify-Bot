from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from bot.database.models import User
from bot.services.spotify import get_spotify_client, like_track, search_tracks, get_track_info

router = Router()


# /search команда
@router.message(F.text.startswith("/search"))
async def search_command(message: Message):
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

    # Клавиатура с кнопками треков
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{track['artist']} — {track['name']}",
            callback_data=f"track_select:{track['id']}"
        )] for track in tracks
    ])

    await message.answer("🔍 Найденные треки:", reply_markup=keyboard)


# Обработка выбора трека
@router.callback_query(F.data.startswith("track_select:"))
async def track_select_handler(callback: CallbackQuery):
    track_id = callback.data.split(":")[1]
    user = await User.get_or_none(telegram_id=callback.from_user.id)

    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    track = await get_track_info(user, track_id)
    if not track:
        await callback.answer("❌ Не удалось получить информацию", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Воспроизвести", callback_data=f"play:{track_id}")],
        [InlineKeyboardButton(text="❤️ Лайкнуть", callback_data=f"like:{track_id}")],
        [InlineKeyboardButton(text="➕ В очередь", callback_data=f"queue:{track_id}")]
    ])

    await callback.message.answer(
        f"*{track['name']}* — {track['artist']}",
        parse_mode="Markdown",
        reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("queue:"))
async def queue_track_handler(callback: CallbackQuery):
    track_id = callback.data.split(":")[1]
    user = await User.get_or_none(telegram_id=callback.from_user.id)

    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    from bot.services.spotify import add_track_to_queue
    success, message = await add_track_to_queue(user, track_id)

    await callback.answer(message, show_alert=not success)


@router.callback_query(F.data.startswith("play:"))
async def play_track_handler(callback: CallbackQuery):
    track_id = callback.data.split(":")[1]
    user = await User.get_or_none(telegram_id=callback.from_user.id)

    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    from bot.services.spotify import play_track
    success, message = await play_track(user, track_id)

    await callback.answer(message, show_alert=not success)


# Обработка лайка
@router.callback_query(F.data.startswith("like:"))
async def like_track_handler(callback: CallbackQuery):
    track_id = callback.data.split(":")[1]
    user = await User.get_or_none(telegram_id=callback.from_user.id)

    if not user or not user.spotify_access_token:
        await callback.answer("⚠️ Авторизация не найдена", show_alert=True)
        return

    success = await like_track(user, track_id)
    if success:
        await callback.answer("❤️ Добавлено в избранное!")
    else:
        await callback.answer("❌ Ошибка при добавлении", show_alert=True)
