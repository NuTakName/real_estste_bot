import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from loguru import logger

from config import settings
from notifiers.logging import NotificationHandler


params = {
    "token": settings["logger"]["logger_telegram_token"],
    "chat_id": settings["logger"]["logger_telegram_chat_id"],
}

logging.basicConfig(
    format="%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s",
    level=logging.ERROR,
)

handler = NotificationHandler("telegram", params)
logger.add(handler, level="ERROR", backtrace=True)

bot = Bot(token=settings["main"]["token"], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()