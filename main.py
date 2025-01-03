# main.py
# new Commit
# Commit and Push
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Update
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types.error_event import ErrorEvent

from config import BOT_TOKEN, GOOGLE_CREDS_FILE, SPREADSHEET_ID
from services.google_api import GoogleSheetsService

# Наши хендлеры
from handlers import registration, admin
print("Hello")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

async def set_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать работу (регистрация)"),
    ])

async def global_error_handler(event: ErrorEvent) -> bool:
    exc = event.exception
    update = event.update

    logging.exception(">>> [GLOBAL ERROR] неперехваченная ошибка: %s", exc)
    if update and update.message:
        try:
            await update.message.answer(f"Глобальная ошибка: {exc}")
        except:
            pass
    elif update and update.callback_query:
        try:
            await update.callback_query.message.answer(f"Глобальная ошибка: {exc}")
        except:
            pass

    return True

async def main():
    logging.info(">>> [MAIN] Запуск бота EkspHesabBot...")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.errors.register(global_error_handler)

    google_service = GoogleSheetsService(GOOGLE_CREDS_FILE, SPREADSHEET_ID)
    google_service.authorize()
    google_service.load_users()

    dp["google_service"] = google_service

    # Подключаем роутеры
    dp.include_router(registration.router)
    dp.include_router(admin.router)

    await set_commands(bot)

    logging.info(">>> [MAIN] Бот запущен. Ожидаем сообщения...")
    try:
        await dp.start_polling(bot)
    finally:
        logging.info(">>> [MAIN] Остановка бота.")
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
