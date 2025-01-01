# handlers/common.py

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "/start — начать работу\n"
        "/help — помощь\n"
        "Доступные роли: admin, expeditor, buyer (пока в базовом виде)\n"
    )
    await message.answer(text)
