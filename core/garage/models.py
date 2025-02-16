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
from core.users.models import User
from core.houses.models import House
from core.flats.models import Flat


class Garage(BaseModel):

    __tablename__ = "garages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    city: Mapped[str] = mapped_column(String(250), nullable=True)
    district: Mapped[str] = mapped_column(String(250), nullable=True)
    info: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=True)
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
            query = await session.execute(select(Garage).where(Garage.id == self.id))
            garage: Garage = query.scalars().first()
            garage.city = self.city
            garage.district = self.district
            garage.info = self.info
            garage.price = self.price
            garage.photos = self.photos
            garage.updated_at = datetime.now()
            garage.phone = self.phone
            garage.address = self.address
            garage.verification = self.verification
            await session.commit()
            kafka_produces = CacheUpdateProducer()
            await kafka_produces.update_cache_unconfirmed_ads()
            await kafka_produces.update_cache_my_ads()
            await kafka_produces.update_cache(current_id=self.id, type_="garage")


    @staticmethod
    async def add_all(garages: list):
        async with async_session() as session:
            session.add_all(garages)
            await session.commit()
            kafka_sending = CacheUpdateProducer()
            await kafka_sending.update_cache_unconfirmed_ads()


    async def confirmed_ads(self) -> "Garage":
        async with async_session() as session:
            query = await session.execute(select(Garage).where(Garage.id == self.id))
            garage: Garage = query.scalars().first()
            garage.updated_at = datetime.now()
            garage.verification = True
            await session.commit()
            kafka_produces = CacheUpdateProducer()
            await kafka_produces.update_cache(garage.id, type_="garage")
            return self


    @staticmethod
    async def get_by_id(garage_id: int) -> "Garage":
        async with async_session() as session:
            result = await session.execute(
                select(Garage).where(Garage.id == garage_id)
            )
            return result.scalars().first()


    @staticmethod
    async def get_garages() -> tuple[dict, dict]:
        async with async_session() as session:
            query = await session.execute(
                select(Garage).where(and_(
                    Garage.verification,
                    Garage.sale,
                    func.jsonb_array_length(Garage.photos) > 0
                ))
            )
            sale: list["Garage"] = query.scalars().all()
            sale_garages = {}
            rent_garages = {}
            for garage in sale:
                sale_garages[garage.id] = garage
            query = await session.execute(
                select(Garage).where(and_(Garage.verification, Garage.rent))
            )
            rent: list["Garage"] = query.scalars().all()
            for garage in rent:
                rent_garages[garage.id] = garage
            return sale_garages, rent_garages


    @staticmethod
    async def get_ads() -> dict[int, list]:
        async with async_session() as session:
            result = await session.execute(
                select(User, Garage, House, Flat)
                .outerjoin(Garage, Garage.user_id == User.user_id)
                .outerjoin(House, House.user_id == User.user_id)
                .outerjoin(Flat, Flat.user_id == User.user_id)
                .distinct()
            )
            records = result.all()
            user_ads = {}
            for user, garage, house, flat in records:
                user_id = user.user_id
                if user_id not in user_ads:
                    user_ads[user_id] = []
                if garage and garage not in user_ads[user_id]:
                    user_ads[user_id].append(garage)
                if house and house not in user_ads[user_id]:
                    user_ads[user_id].append(house)
                if flat and flat not in user_ads[user_id]:
                    user_ads[user_id].append(flat)
            return user_ads


    @staticmethod
    async def get_unconfirmed_ads() -> list:
        async with async_session() as session:
            result = await session.execute(
                select(User, Garage, House, Flat)
                .outerjoin(Garage, Garage.user_id == User.user_id)
                .outerjoin(House, House.user_id == User.user_id)
                .outerjoin(Flat, Flat.user_id == User.user_id)
            )
            res = result.all()
            unconfirmed_ads = set()
            for user, garage, house, flat in res:
                if garage and not garage.verification and len(garage.photos) > 0:
                    unconfirmed_ads.add(garage)
                if house and not house.verification and len(house.photos) > 0:
                    unconfirmed_ads.add(house)
                if flat and not flat.verification and len(flat.photos) > 0:
                    unconfirmed_ads.add(flat)
            return list(unconfirmed_ads)
