from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from middlewares.role_required import RoleRequiredMiddleware

router = Router()
router.message.middleware(RoleRequiredMiddleware(["admin", "expeditor"]))

@router.message(Command("add_receipt"))
async def cmd_add_receipt(message: Message, google_service):
    """
    Упрощённая версия /add_receipt.
    Пример использования: /add_receipt <Товар> <Кол-во>
    """
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Формат: /add_receipt <Товар> <Кол-во>")
        return

    product_name = parts[1]
    try:
        quantity = int(parts[2])
    except ValueError:
        await message.answer("Количество должно быть числом!")
        return

    expeditor_name = message.from_user.username or message.from_user.full_name
    google_service.add_receipt(expeditor_name, product_name, quantity)

    await message.answer(f"Поступление добавлено:\nТовар: {product_name}\nКол-во: {quantity}")
