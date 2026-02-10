from aiogram import Router
from aiogram.types import Message
from config import ADMIN_ID

router = Router()

@router.message()
async def any_message(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ запрещён")
        return

    await message.answer("✅ Ты админ")
