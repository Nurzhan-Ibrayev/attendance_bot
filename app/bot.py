import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db import init_db

from handlers.attendance import router as attendance_router
from handlers.registration import router as registration_router
from handlers.teacher import router as teacher_router


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(registration_router)
    dp.include_router(attendance_router)
    dp.include_router(teacher_router)
    
    init_db()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
