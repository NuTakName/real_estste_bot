import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from celery import Celery
from celery.signals import worker_process_init

from config import settings
from loguru import logger

from core.users.models import User, Admin
from parser.vdnd.vdnd import VdndParser

app = Celery(
    "main_tasks",
    broker=settings["celery"]["broker"],
    include=["main"],
    task_track_started=True,
)



@worker_process_init.connect
def init_worker(**kwargs):
    global loop
    loop = asyncio.new_event_loop()
    asyncio.sleep(0.05)
    asyncio.set_event_loop(loop)


@app.task()
def parse_estate_and_send_message_after_finish(uid: int):
    parser=VdndParser()
    finish_parsing = loop.run_until_complete(parser.run())
    if finish_parsing:
        bot = Bot(token=settings["main"]["token"])
        loop.run_until_complete(bot.send_message(
            chat_id=uid,
            text=f"Парсинг недвижимости завершен\n"
                 f" Перейдите в соответсвующее меню, чтобы подтвердить или отклонить объявление")
        )
        loop.run_until_complete(bot.session.close())



@app.task()
def send_notification_about_rejected_or_confirmed_ads(
        user_id: int,
        admin_username: str | None = None,
        reason: str | None = None,
        ads_name: str | None = None,
        confirmed: bool | None = False
):
    token = settings["main"]["token"]
    bot = Bot(token=token)
    user: User = loop.run_until_complete(User.get(uid=user_id))
    admin_ids: Admin = loop.run_until_complete(Admin.get_admin_user_ids())
    if user and user.user_setting.notification and user_id not in admin_ids:
        try:
            if not confirmed:
                text = f"Администратор @{admin_username} отклонил ваше объявление {ads_name} по причине {reason}"
            else:
                text = "Ваше объявление подтвердил администратор. Теперь оно появится в общей ленте"
            loop.run_until_complete(
                bot.send_message(chat_id=user_id, text=text)
            )
        except TelegramBadRequest as e:
            logger.warning(e)
    loop.run_until_complete(bot.session.close())


