import asyncio

from loguru import logger
from aiogram.types import BotCommand

from cache_updater.kafka_consumer import CacheSupervisor
from cache_updater.kafka_sender import CacheUpdateProducer
from cached_data.cached_flat import CachedFlat
from cached_data.cached_garage import CachedGarage
from cached_data.cached_house import CachedHouse
from cached_data.cached_my_ads import CachedAds
from cached_data.cached_unconfirmed_ads import UnconfirmedAds
from handlers import (
    error_handler,
    main_handler,
    sell_or_rent_flat_handler,
    sell_or_rent_house_handler,
    sell_or_rent_garage_handler,
    buy_or_pass_flat_handler,
    buy_or_pass_house_handler,
    buy_or_pass_garage_handler,
    my_ads_handler,
    admin_hendler,
    parser_ads_handler,
    settings_handler
)
from middlewares.registration_middleware import RegistrationMiddleware
from middlewares.user_injector_middleware import UserInjectorMiddleware
from misc import bot, dp


async def set_bot_commands():
    commands = [BotCommand(command="start", description="Начать работу")]
    await bot.set_my_commands(commands)

async def on_startup():
    kafka_consumer = CacheSupervisor()
    await kafka_consumer.subscribe()


async def on_shutdown():
    cache_update_producer = CacheUpdateProducer()
    await cache_update_producer.producer_stop()
    logger.warning("Stop polling bot")


async def loads_data():
    cached_flat = CachedFlat()
    cached_house = CachedHouse()
    cached_garage = CachedGarage()
    unconfirmed_ads = UnconfirmedAds()
    my_ads = CachedAds()
    tasks = [
        cached_flat.loads_data_flats(),
        cached_house.loads_data_houses(),
        cached_garage.loads_data_garages(),
        unconfirmed_ads.loads_data(),
        my_ads.loads_data()
    ]
    await asyncio.gather(*tasks)

async def main():
    await set_bot_commands()
    await loads_data()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.outer_middleware.register(RegistrationMiddleware())
    dp.message.middleware.register(UserInjectorMiddleware())
    dp.callback_query.middleware.register(UserInjectorMiddleware())
    dp.include_router(error_handler.router)
    dp.include_router(main_handler.router)
    dp.include_router(sell_or_rent_flat_handler.router)
    dp.include_router(sell_or_rent_house_handler.router)
    dp.include_router(sell_or_rent_garage_handler.router)
    dp.include_router(buy_or_pass_flat_handler.router)
    dp.include_router(buy_or_pass_house_handler.router)
    dp.include_router(buy_or_pass_garage_handler.router)
    dp.include_router(my_ads_handler.router)
    dp.include_router(admin_hendler.router)
    dp.include_router(parser_ads_handler.router)
    dp.include_router(settings_handler.router)
    bot_info = await bot.get_me()
    logger.warning(f"{bot_info.username} start polling bot")
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())