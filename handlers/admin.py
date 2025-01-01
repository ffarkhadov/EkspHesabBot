# handlers/admin.py

"""
Обработка inline-кнопок "approve_buyer:..." и "decline_buyer:..."
Требуется, чтобы только admin мог нажать эти кнопки (см. RoleRequiredMiddleware).
"""

from aiogram import Router
from aiogram.types import CallbackQuery
from middlewares.role_required import RoleRequiredMiddleware
from datetime import datetime

router = Router()

# Применим мидлвару для колбэков: только admin может нажать
router.callback_query.middleware(RoleRequiredMiddleware(["admin"]))

@router.callback_query(lambda c: c.data.startswith("approve_buyer"))
async def callback_approve_buyer(call: CallbackQuery, google_service):
    """
    approve_buyer:<user_id>:<store_name>:<region>:<phone>
    """
    parts = call.data.split(":")
    if len(parts) < 5:
        await call.answer("Неверный формат callback_data.")
        return

    _, user_id_str, store_name, region, phone = parts
    user_id = int(user_id_str)

    # Здесь username может быть пустым (не Telegram username, а имя магазина)
    # Или можем вытащить call.from_user.username, но это username АДМИНА,
    # нам нужен username пользователя — у нас его нет.
    # Считаем, что username = "unknown" или user_id
    username_for_buyer = f"unknown_{user_id_str}"

    # Записываем в таблицу (role=buyer, is_active=True)
    google_service.add_buyer(
        user_id=user_id,
        username=username_for_buyer,
        store_name=store_name,
        region=region,
        phone=phone
    )

    await call.message.answer("Пользователь добавлен в Google Sheets как buyer!")
    # Оповестим самого пользователя
    try:
        await call.message.bot.send_message(
            user_id,
            "Ваша заявка одобрена! Теперь вы можете пользоваться ботом."
        )
    except:
        pass

    await call.answer("Заявка подтверждена.", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("decline_buyer"))
async def callback_decline_buyer(call: CallbackQuery, google_service):
    """
    decline_buyer:<user_id>
    """
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer("Неверный формат callback_data.")
        return

    _, user_id_str = parts
    user_id = int(user_id_str)

    await call.message.answer(f"Заявка пользователя user_id={user_id} отклонена.")
    # Оповестим самого пользователя
    try:
        await call.message.bot.send_message(
            user_id,
            "Извините, ваша заявка отклонена администратором."
        )
    except:
        pass

    await call.answer("Заявка отклонена.", show_alert=True)
