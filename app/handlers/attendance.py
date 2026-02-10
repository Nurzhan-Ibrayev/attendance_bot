from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import get_user, add_attendance
from handlers.registration import Registration

router = Router()


class ExcuseFSM(StatesGroup):
    waiting_for_proof = State()


@router.message(lambda m: m.text in [
        "✅ Я на занятии",
        "⏰ Опоздаю",
        "❌ Отсутствую",
    ])
async def mark_attendance(message: Message, state: FSMContext):
    # 1️⃣ Проверка FSM (если вводит имя — игнорируем)
    current_state = await state.get_state()
    if current_state == Registration.waiting_for_name:
        return

    # 2️⃣ Проверка регистрации
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("❗ Сначала зарегистрируйся через /start")
        return

    # 3️⃣ Всё ок — можно отмечаться
    status_map = {
    "✅ Я на занятии": "present",
    "⏰ Опоздаю": "late",
    "❌ Отсутствую": "absent",
}

    status = status_map[message.text]


    success = add_attendance(
        user_id=message.from_user.id,
        status=status
    )

    if not success:
        await message.answer("⚠️ Ты уже отмечался сегодня")
        return

    await message.answer("📌 Отметка сохранена")


@router.message(lambda m: m.text == "📝 По уважительной причине")
async def excuse_start(message: Message, state: FSMContext):
    # проверка регистрации
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("❗ Сначала зарегистрируйся через /start")
        return

    await state.set_state(ExcuseFSM.waiting_for_proof)

    await message.answer(
        "🧾 Пожалуйста, отправь фото или файл, подтверждающий причину отсутствия"
    )

@router.message(ExcuseFSM.waiting_for_proof)
async def handle_excuse_proof(message: Message, state: FSMContext):
    if not (message.photo or message.document):
        await message.answer("❗ Нужен файл или фото")
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    else:
        file_id = message.document.file_id
        file_type = "document"

    success = add_attendance(   
        user_id=message.from_user.id,
        status="excused",
        proof_file_id=file_id,
        proof_type=file_type
    )

    if not success:
        await message.answer("⚠️ Ты уже отмечался сегодня")
        await state.clear()
        return

    await state.clear()
    await message.answer("✅ Отметка с подтверждением сохранена")
