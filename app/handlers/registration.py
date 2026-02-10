from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from db import get_user, add_user
import os

router = Router()


class Registration(StatesGroup):
    waiting_for_name = State()

attendance_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Я на занятии")],
        [KeyboardButton(text="⏰ Опоздаю")],
        [KeyboardButton(text="❌ Отсутствую")],
        [KeyboardButton(text="📝 По уважительной причине")],
    ],
    resize_keyboard=True
)

teacher_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Уважительные причины")]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    from config import ADMIN_ID
    TEACHER_IDS = ADMIN_ID
    # 👨‍🏫 Учитель
    if user_id == TEACHER_IDS:
        await state.clear()
        await message.answer(
            "👨‍🏫 Режим преподавателя",
            reply_markup=teacher_kb
        )
        return

    # 👨‍🎓 Ученик (уже зарегистрирован)
    if user:
        await message.answer(
            f"Ты уже зарегистрирован как {user[1]} 👋\nОтметь посещаемость:",
            reply_markup=attendance_keyboard
        )
        return

    # 👶 Новый ученик
    await message.answer(
        "Привет! Введи своё имя 👇",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.waiting_for_name)


@router.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("Имя слишком короткое, попробуй ещё раз")
        return

    add_user(
        user_id=message.from_user.id,
        name=name,
        username=message.from_user.username
    )

    await state.clear()

    await message.answer(
        f"Готово! Ты зарегистрирован как {name} ✅\nТеперь отметь посещаемость:",
        reply_markup=attendance_keyboard
    )
