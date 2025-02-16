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


class Flat(BaseModel):

    __tablename__ = "flats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    city: Mapped[str] = mapped_column(String(250), nullable=True)
    district: Mapped[str] = mapped_column(String(250), nullable=True)
    rooms: Mapped[int] = mapped_column(Integer, nullable=True)
    the_general_area: Mapped[float] = mapped_column(Float, nullable=True)
    floor: Mapped[int] = mapped_column(Integer, nullable=True)
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
            query = await session.execute(select(Flat).where(Flat.id == self.id))
            flat: Flat = query.scalars().first()
            flat.city = self.city
            flat.district = self.district
            flat.rooms = self.rooms
            flat.the_general_area = self.the_general_area
            flat.floor = self.floor
            flat.info = self.info
            flat.price = self.price
            flat.photos = self.photos
            flat.updated_at = datetime.now()
            flat.phone = self.phone
            flat.address = self.address
            flat.verification = self.verification
            await session.commit()
            kafka_produces = CacheUpdateProducer()
            await kafka_produces.update_cache_unconfirmed_ads()
            await kafka_produces.update_cache_my_ads()
            await kafka_produces.update_cache(current_id=self.id, type_="flat")


    @staticmethod
    async def add_all(flats: list):
        async with async_session() as session:
            session.add_all(flats)
            await session.commit()
            kafka_produces = CacheUpdateProducer()
            await kafka_produces.update_cache_unconfirmed_ads()


    async def confirmed_ads(self) -> "Flat":
        async with async_session() as session:
            query = await session.execute(select(Flat).where(Flat.id == self.id))
            flat: Flat = query.scalars().first()
            flat.updated_at = datetime.now()
            flat.verification = True
            await session.commit()
            kafka_produces = CacheUpdateProducer()
            await kafka_produces.update_cache(flat.id, type_="flat")
            return self




    @staticmethod
    async def get_by_id(flat_id: int) -> "Flat":
        async with async_session() as session:
            result = await session.execute(
                select(Flat).where(Flat.id == flat_id)
            )
            return result.scalars().first()


    @staticmethod
    async def get_flats() -> tuple[dict, dict]:
        async with async_session() as session:
            query = await session.execute(
                select(Flat).where(and_(
                    Flat.verification,
                    Flat.sale,
                    func.jsonb_array_length(Flat.photos) > 0
                ))
            )
            sale: list["Flat"] = query.scalars().all()
            sale_flats = {}
            rent_flats = {}
            for flat in sale:
                sale_flats[flat.id] = flat
            query = await session.execute(
                select(Flat).where(and_(Flat.verification, Flat.rent))
            )
            rent: list["Flat"] = query.scalars().all()
            for flat in rent:
                rent_flats[flat.id] = flat
            return sale_flats, rent_flats
