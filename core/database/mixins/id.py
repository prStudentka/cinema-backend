from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column


class IntegerIdMixin:
    """Миксин, добавляющий id pk"""

    __mapper_args__ = {"always_refresh": False}
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
