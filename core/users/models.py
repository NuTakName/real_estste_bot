from sqlalchemy import Integer, BigInteger, String, select, ForeignKey, Boolean
from enum import Enum as enum

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.async_session import async_session
from core.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(180), nullable=True)
    last_name: Mapped[str] = mapped_column(String(180), nullable=True)
    username: Mapped[str] = mapped_column(String(180), nullable=True)
    phone: Mapped[str] = mapped_column(String(180), nullable=True)
    place: Mapped[str] = mapped_column(String(250), nullable=True)
    user_setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users_setting.id", ondelete="CASCADE"), nullable=False
    )
    user_setting = relationship("UserSetting", lazy="subquery", foreign_keys=[user_setting_id])



    async def add(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self


    async def update(self) -> "User":
        async with async_session() as session:
            query = await session.execute(select(User).where(User.user_id == self.user_id))
            user: User = query.scalars().first()
            print(user.id)
            user.username = self.username
            user.last_name = self.last_name
            user.first_name = self.first_name
            user.phone = self.phone
            await session.commit()
            return self


    @staticmethod
    async def get_user_phone(uid: int) -> str:
        async with async_session() as session:
            result = await session.execute(
                select(User.phone).where(User.user_id == uid)
            )
            return result.scalars().first()


    def get_full_name(self, without_last_name: bool = False):
        name = ""
        if self.first_name:
            name += self.first_name
        if self.last_name is not None and not without_last_name:
            name += f" {self.last_name}"
        return name


    @staticmethod
    async def get(uid: int) -> "User":
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.user_id == uid)
            )
            return result.scalars().first()


    @staticmethod
    async def get_users() -> dict:
        async with async_session() as session:
            query = await session.execute(
                select(User, Admin)
                .outerjoin(Admin, User.id == Admin.user_id)
            )
            results = query.all()
            users = {}
            for user, admin in results:
                u = user.to_dict()
                u["admin"] = True if admin else False
                users[user.user_id] = u
            return users




class Admin(BaseModel):

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)


    @staticmethod
    async def get_admin() -> "Admin":
        async with async_session() as session:
            result = await session.execute(
                select(Admin)
            )
            return result.scalars().first()

    @staticmethod
    async def get_admin_user_id() -> int:
        async with async_session() as session:
            result = await session.execute(
                select(User.user_id)
                .join(Admin, Admin.user_id == User.id)
            )
            return result.scalars().first()


    @staticmethod
    async def get_admin_user_ids() -> list[int]:
        async with async_session() as session:
            result = await session.execute(
                select(Admin.user_id)
            )
            return result.scalars().all()

class CurrencyType(str, enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class UserSetting(BaseModel):


    __tablename__ = "users_setting"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[CurrencyType] = mapped_column(
        ENUM(CurrencyType, name="currency"),
        nullable=False,
        default=CurrencyType.RUB
    )
    notification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


    async def update(self) -> "User":
        async with async_session() as session:
            query = await session.execute(select(UserSetting).where(UserSetting.user_id == self.user_id))
            user_setting: UserSetting = query.scalars().first()
            user_setting.user_id = self.user_id
            user_setting.currency = self.currency
            user_setting.notification = self.notification
            await session.commit()
            return self


    @staticmethod
    async def get_by_user_id(uid: int) -> "UserSetting":
        async with async_session() as session:
            result = await session.execute(
                select(UserSetting).where(UserSetting.user_id == uid)
            )
            return result.scalars().first()



