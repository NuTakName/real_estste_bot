from typing import Callable, Any, Awaitable
from venv import logger

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.users.models import User



class UserInjectorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        users = await User.get_users()
        user = users.get(event.from_user.id)
        if user:
            admin = user.pop("admin")
            user = User(**user)
            data["user"] = user
            data["admin"] = admin
        else:
            logger.error(f"Незарегистрированный пользователь {event.from_user.id}")
        return await handler(event, data)

