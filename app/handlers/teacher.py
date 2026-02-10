import os
from aiogram import Router, Bot
from aiogram.types import Message

from db import get_excused_attendance

router = Router()



@router.message(lambda m: m.text == "📋 Уважительные причины")
async def show_excused(message: Message, bot: Bot):
    from config import ADMIN_ID
    TEACHER_IDS = ADMIN_ID
    if message.from_user.id != TEACHER_IDS:
        await message.answer("❌ Доступ запрещён")
        return

    records = get_excused_attendance()

    if not records:
        await message.answer("📭 Пока нет уважительных причин")
        return

    for name, day, file_id, file_type in records:
        caption = f"👤 {name}\n📅 {day}"

        if file_type == "photo":
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=file_id,
                caption=caption
            )
        else:
            await bot.send_document(
                chat_id=message.chat.id,
                document=file_id,
                caption=caption
            )
