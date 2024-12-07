from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum

from core.database import Base
from core.database.mixins import IntegerIdMixin, TimeStampMixin
from core.enums.users import RoleKindEnum


class User(Base, IntegerIdMixin, TimeStampMixin):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    role: Mapped[RoleKindEnum] = mapped_column(
        Enum(RoleKindEnum), default=RoleKindEnum.CLIENT, nullable=False
    )

    __mapper_args__ = {"eager_defaults": True}
