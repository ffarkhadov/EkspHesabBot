# middlewares/role_required.py

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Awaitable, Callable, Dict

class RoleRequiredMiddleware(BaseMiddleware):
    """
    Мидлвара, разрешающая доступ к хендлеру,
    только если user_id есть в users_cache
    и role входит в allowed_roles.
    """
    def __init__(self, allowed_roles: list[str]):
        super().__init__()
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        google_service = data.get("google_service")
        if not google_service:
            await event.answer("Ошибка: нет GoogleSheetsService.")
            return

        user_id = event.from_user.id
        user_info = google_service.users_cache.get(user_id)

        if not user_info:
            await event.answer("У вас нет прав. Вы не зарегистрированы.")
            return

        role = user_info.get("role", "buyer")
        if role not in self.allowed_roles:
            await event.answer("Недостаточно прав для этого действия.")
            return

        return await handler(event, data)
