from datetime import datetime

from sqlalchemy import (
    Integer,
    BigInteger,
    ForeignKey,
    String,
    Float,
    Text,
    DateTime,
    BOOLEAN,
    select,
    and_,
    func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from cache_updater.kafka_sender import CacheUpdateProducer
from core import BaseModel, async_session


class House(BaseModel):

    __tablename__ = "houses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=True
    )
    city: Mapped[str] = mapped_column(String(250), nullable=True)
    district: Mapped[str] = mapped_column(String(250), nullable=True)
    rooms: Mapped[int] = mapped_column(Integer, nullable=True)
    the_general_area: Mapped[float] = mapped_column(Float, nullable=True)
    info: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=True, index=True)
    photos: Mapped[dict] = mapped_column(JSONB, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    sale: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    rent: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    verification: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    user_name: Mapped[str] = mapped_column(String, nullable=True)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)


    async def update(self):
        async with async_session() as session:
            query = await session.execute(select(House).where(House.id == self.id))
            house: House = query.scalars().first()
            house.city = self.city
            house.district = self.district
            house.rooms = self.rooms
            house.the_general_area = self.the_general_area
            house.info = self.info
            house.price = self.price
            house.photos = self.photos
            house.updated_at = datetime.now()
            house.phone = self.phone
            house.address = self.address
            house.verification = self.verification
            await session.commit()
            kafka_produces = CacheUpdateProducer()
            await kafka_produces.update_cache_unconfirmed_ads()
            await kafka_produces.update_cache_my_ads()
            await kafka_produces.update_cache(current_id=self.id, type_="house")

    @staticmethod
    async def add_all(houses: list):
        async with async_session() as session:
            session.add_all(houses)
            await session.commit()
            kafka_sending = CacheUpdateProducer()
            await kafka_sending.update_cache_unconfirmed_ads()


    async def confirmed_ads(self) -> "House":
        async with async_session() as session:
            query = await session.execute(select(House).where(House.id == self.id))
            house: House = query.scalars().first()
            house.updated_at = datetime.now()
            house.verification = True
            await session.commit()
            kafka_produces = CacheUpdateProducer()
            await kafka_produces.update_cache(house.id, type_="house")
            return self


    @staticmethod
    async def get_by_id(house_id: int) -> "House":
        async with async_session() as session:
            result = await session.execute(
                select(House).where(House.id == house_id)
            )
            return result.scalars().first()


    @staticmethod
    async def get_houses() -> tuple[dict, dict]:
        async with async_session() as session:
            query = await session.execute(
                select(House).where(and_(
                    House.verification,
                    House.sale,
                    func.jsonb_array_length(House.photos) > 0
                ))
            )
            sale: list["House"] = query.scalars().all()
            sale_houses = {}
            rent_houses = {}
            for house in sale:
                sale_houses[house.id] = house
            query = await session.execute(
                select(House).where(and_(House.verification, House.rent))
            )
            rent: list["House"] = query.scalars().all()
            for house in rent:
                rent_houses[house.id] = house
            return sale_houses, rent_houses

