from aiogram import Router, types, F

from callbacks import SearchAdsCallbackData
from main import parse_estate_and_send_message_after_finish

router = Router()

@router.callback_query(SearchAdsCallbackData.filter(F.action == "find_ads"))
async def find_ads(callback: types.CallbackQuery):
    parse_estate_and_send_message_after_finish.apply_async(args=(callback.from_user.id,))
    await callback.answer("Парсинг сайта запущен, ожидайте уведомления о завершении")

