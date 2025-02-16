from datetime import datetime
from enum import Enum as enum
from sqlalchemy import Integer, BigInteger, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import  ENUM
from sqlalchemy.orm import Mapped, mapped_column

from core import BaseModel, async_session




class AdsType(str, enum):
    flat = "flat"
    house = "house"
    garage = "garage"


class RejectedAds(BaseModel):

    __tablename__ = "rejected_ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type_: Mapped[AdsType] = mapped_column(ENUM(AdsType, name="ads_type"), nullable=False)
    flat_id: Mapped[int] = mapped_column(Integer, ForeignKey("flats.id", ondelete="CASCADE"), index=True, nullable=True)
    house_id: Mapped[int] = mapped_column(Integer, ForeignKey("houses.id", ondelete="CASCADE"), index=True, nullable=True)
    garage_id: Mapped[int] = mapped_column(Integer, ForeignKey("garages.id", ondelete="CASCADE"), index=True, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())


    async def add(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self

