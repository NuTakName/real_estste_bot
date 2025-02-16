import asyncio
from json import loads

from loguru import logger
from aiokafka import AIOKafkaConsumer

from cache_updater.kafka_topic import KafkaTopics
from cached_data.cached_flat import CachedFlat
from cached_data.cached_garage import CachedGarage
from cached_data.cached_house import CachedHouse
from cached_data.cached_my_ads import CachedAds
from cached_data.cached_unconfirmed_ads import UnconfirmedAds
from cached_data.sigleton import Singleton
from config import settings


class CacheSupervisor(metaclass=Singleton):

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        if not self.loop:
            self.loop = asyncio.new_event_loop()


    async def consume_reload_flats(self):
        consumer = AIOKafkaConsumer(
            KafkaTopics.RELOAD_FLATS.value,
            loop=self.loop,
            bootstrap_servers=settings["main"]["KAFKA_BOOTSTRAP_SERVERS"],
            group_id="core",
        )
        await consumer.start()
        try:
            async for msg in consumer:
                logger.warning(f"Кафка перезагружает кэш квартир")
                cache = CachedFlat()
                await cache.loads_data_flats()
        finally:
            await consumer.stop()


    async def consume_reload_houses(self):
        consumer = AIOKafkaConsumer(
            KafkaTopics.RELOAD_HOUSES.value,
            loop=self.loop,
            bootstrap_servers=settings["main"]["KAFKA_BOOTSTRAP_SERVERS"],
            group_id="core",
        )
        await consumer.start()
        try:
            async for msg in consumer:
                logger.warning(f"Кафка перезагружает кэш домов")
                cache = CachedHouse()
                await cache.loads_data_houses()
        finally:
            await consumer.stop()


    async def consume_reload_garages(self):
        consumer = AIOKafkaConsumer(
            KafkaTopics.RELOAD_GARAGES.value,
            loop=self.loop,
            bootstrap_servers=settings["main"]["KAFKA_BOOTSTRAP_SERVERS"],
            group_id="core",
        )
        await consumer.start()
        try:
            async for msg in consumer:
                logger.warning(f"Кафка перезагружает кэш гаражей")
                cache = CachedGarage()
                await cache.loads_data_garages()
        finally:
            await consumer.stop()


    async def consume_reload_unconfirmed_ads(self):
        consumer = AIOKafkaConsumer(
            KafkaTopics.RELOAD_UNCONFIRMED_ADS.value,
            loop=self.loop,
            bootstrap_servers=settings["main"]["KAFKA_BOOTSTRAP_SERVERS"],
            group_id="core",
        )
        await consumer.start()
        try:
            async for msg in consumer:
                logger.warning(f"Кафка перезагружает кэш неподтвержденных записей")
                cache = UnconfirmedAds()
                await cache.loads_data()
        finally:
            await consumer.stop()


    async def consume_reload_my_ads(self):
        consumer = AIOKafkaConsumer(
            KafkaTopics.RELOAD_ADS.value,
            loop=self.loop,
            bootstrap_servers=settings["main"]["KAFKA_BOOTSTRAP_SERVERS"],
            group_id="core",
        )
        await consumer.start()
        try:
            async for msg in consumer:
                logger.warning(f"Кафка перезагружает кэш объявлений пользователя")
                cache = CachedAds()
                await cache.loads_data()
        finally:
            await consumer.stop()


    async def subscribe(self):
        asyncio.create_task(self.consume_reload_flats())
        asyncio.create_task(self.consume_reload_houses())
        asyncio.create_task(self.consume_reload_garages())
        asyncio.create_task(self.consume_reload_unconfirmed_ads())
        asyncio.create_task(self.consume_reload_my_ads())
        logger.warning("Kafka connected")
