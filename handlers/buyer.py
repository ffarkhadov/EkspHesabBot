from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from middlewares.role_required import RoleRequiredMiddleware

router = Router()
router.message.middleware(RoleRequiredMiddleware(["buyer", "admin"]))

@router.message(Command("order"))
async def cmd_order(message: Message):
    await message.answer("Здесь будет логика оформления заказа (для buyer).")
