from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.users.models import User, UserSetting


class RegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from_user = None
        if event.message:
            from_user = event.message.from_user
        elif event.callback_query:
            from_user = event.callback_query.from_user
        user = await User.get(uid=from_user.id)
        if not user:
            user_settings = UserSetting(
                user_id=from_user.id,
            )
            user_settings = await user_settings.add()
            user = User(
                user_id=from_user.id,
                first_name=from_user.first_name,
                last_name=from_user.last_name,
                username=from_user.username,
                user_setting_id=user_settings.id
            )
            await user.add()
        return await handler(event, data)
