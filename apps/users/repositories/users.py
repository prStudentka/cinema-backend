from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from apps.users.models.users import User
from core.database import Propagation, Transactional
from core.repositories.base import BaseORMRepository


@dataclass
class BaseUserRepository:
    @abstractmethod
    async def create(
        self, attributes: dict[str, Any] = None
    ) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Iterable[User] | None: ...

    @abstractmethod
    async def get_by_id(self, id_: int) -> User | None: ...

    @abstractmethod
    async def get_by_filter(
        self,
        field: str,
        value: Any,
        join_: set[str, Any] = None,
        order_: dict | None = None,
    ) -> Iterable[User] | list[None]: ...


@dataclass
class ORMUserRepository(BaseUserRepository, BaseORMRepository[User]):
    @Transactional(propagation=Propagation.REQUIRED)
    async def create(self, attributes: dict[str, Any] = None) -> User | None:
        return await super(BaseUserRepository, self).create(
            attributes=attributes
        )

    async def get_by_email(self, email: str) -> Iterable[User] | None:
        return await self.get_by(field="email", value=email)

    async def get_by_id(self, id_: int) -> User | None:
        return await self.get_by(field="id", value=id_)

    async def get_by_filter(
        self,
        field: str,
        value: Any,
        join_: set[str, Any] = None,
        order_: dict | None = None,
    ) -> Iterable[User] | list[None]:
        return await self.get_by(field=field, value=value, join_=join_)
