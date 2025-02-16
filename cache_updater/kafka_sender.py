import asyncio
import time
from pydoc_data.topics import topics

from sqlalchemy.ext.serializer import dumps

from config import settings

from cache_updater.kafka_topic import KafkaTopics
from cached_data.sigleton import Singleton

from loguru import logger
from aiokafka import AIOKafkaProducer


class CacheUpdateProducer(metaclass=Singleton):


    def __init__(self):
        self.loop = asyncio.get_event_loop()
        if not self.loop:
            self.loop = asyncio.new_event_loop()
        self.producer = None


    async def producer_start(self):
        if not self.producer:
            self.producer = AIOKafkaProducer(
                loop=self.loop, bootstrap_servers=settings["main"]["kafka_bootstrap_servers"]
            )
            await self.producer.start()


    async def producer_stop(self):
        if self.producer:
            await self.producer.stop()
            self.producer = None


    async def update_cache(self, current_id: int, type_: str):
        await self.producer_start()
        if type_ == "flat":
            topic = KafkaTopics.RELOAD_FLATS.value
        elif type_ == "house":
            topic = KafkaTopics.RELOAD_HOUSES.value
        else:
            topic = KafkaTopics.RELOAD_GARAGES.value
        await self.producer.send(topic=topic, value=dumps(current_id))


    async def update_cache_unconfirmed_ads(self):
        await self.producer_start()
        logger.warning("Что-то добавили, перезагружаю кэш")
        await self.producer.send(topic=KafkaTopics.RELOAD_UNCONFIRMED_ADS.value, value=dumps(time.time()))


    async def update_cache_my_ads(self):
        await self.producer_start()
        logger.warning("Перезагружаем записей пользователей")
        await self.producer.send(topic=KafkaTopics.RELOAD_ADS.value, value=dumps(time.time()))
