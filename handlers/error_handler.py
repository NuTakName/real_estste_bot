from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger
from traceback import format_exc

router = Router()


@router.error()
async def error_handler(event: ErrorEvent):
    bot_info = await event.update.bot.get_me()
    logger.error(f"@{bot_info.username}\n{format_exc()}"[-4000:])