# handlers/registration.py

from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID

router = Router()

# Список районов (code, label)
REGIONS = [
    ("Binəqədi", "Бинагадинский район"),
    ("Qaradağ", "Гарадагский район"),
    ("Xətai", "Хатаинский район"),
    ("Xəzər", "Хазарский район"),
    ("Nərimanov", "Назиминский район (Nərimanov)"),
    ("Nizami", "Назиминский район (Nizami)"),
    ("Sabunçu", "Сабунчинский район"),
    ("Səbail", "Сабайльский район"),
    ("Suraxanı", "Сураханский район"),
    ("Yasamal", "Ясамальский район"),
    ("Pirallahı", "Пираллахинский район"),
]

class BuyerRegistration(StatesGroup):
    waiting_for_store_name = State()
    waiting_for_region = State()
    waiting_for_phone = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, google_service):
    """
    При /start проверяем, есть ли user_id в кэше.
    Если есть — бот приветствует и сообщает роль.
    Если нет — предлагаем пройти заявку на buyer.
    """
    user_id = message.from_user.id
    users_cache = google_service.users_cache

    if user_id in users_cache:
        user_data = users_cache[user_id]
        role = user_data.get("role", "buyer")
        await message.answer(f"Добро пожаловать! Ваша роль: {role}.")
        return

    # Нет в кэше -> начинаем сбор заявки
    await message.answer("Вы не зарегистрированы.\nВведите название магазина:")
    await state.set_state(BuyerRegistration.waiting_for_store_name)

@router.message(BuyerRegistration.waiting_for_store_name)
async def process_store_name(message: Message, state: FSMContext):
    """
    Шаг 1: запрашиваем store_name, затем предлагаем выбрать район (inline-кнопки).
    """
    store_name = message.text.strip()
    await state.update_data(store_name=store_name)

    # Формируем inline-кнопки районов
    buttons = []
    for code, label in REGIONS:
        btn = InlineKeyboardButton(text=label, callback_data=f"choose_region:{code}")
        buttons.append([btn])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите ваш район:", reply_markup=markup)
    await state.set_state(BuyerRegistration.waiting_for_region)

@router.callback_query(lambda c: c.data.startswith("choose_region"), BuyerRegistration.waiting_for_region)
async def process_choose_region(callback: CallbackQuery, state: FSMContext):
    """
    Шаг 2: пользователь выбрал район из inline-кнопок, переходим к запросу телефона.
    """
    parts = callback.data.split(":")
    if len(parts) < 2:
        await callback.answer("Ошибка данных.")
        return

    region_code = parts[1]
    await state.update_data(region=region_code)

    await callback.message.edit_reply_markup()  # убираем кнопки
    await callback.message.answer("Введите контактный телефон:")
    await state.set_state(BuyerRegistration.waiting_for_phone)

    await callback.answer()  # закроем "загрузка" у Telegram

@router.message(BuyerRegistration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext, google_service):
    """
    Шаг 3: получаем телефон, отправляем админу заявку.
    """
    phone = message.text.strip()
    data = await state.get_data()

    store_name = data["store_name"]
    region = data["region"]

    # Формируем сообщение админу
    admin_text = (
        f"Новая заявка на роль Buyer!\n"
        f"Магазин: {store_name}\n"
        f"Район: {region}\n"
        f"Телефон: {phone}\n\n"
        f"UserID: {message.from_user.id}\n"
        "Подтвердить заявку?"
    )

    # Добавим inline-кнопки «Подтвердить» и «Отклонить»
    approve_button = InlineKeyboardButton(
        text="Подтвердить",
        callback_data=f"approve_buyer:{message.from_user.id}:{store_name}:{region}:{phone}"
    )
    decline_button = InlineKeyboardButton(
        text="Отклонить",
        callback_data=f"decline_buyer:{message.from_user.id}"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[approve_button, decline_button]])

    # Уведомляем пользователя
    await message.answer("Ваша заявка отправлена админу. Ожидайте ответа.")
    # Сбрасываем состояние
    await state.clear()

    # Отправляем админу
    await message.bot.send_message(ADMIN_ID, admin_text, reply_markup=markup)
