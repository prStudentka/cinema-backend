from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from apps.users.exceptions.users import UserNotFoundException
from apps.users.models.users import User
from apps.users.repositories.users import BaseUserRepository
from core.security.password import PasswordHandler
from core.services.base import BaseOrmService


@dataclass
class BaseUserService:
    repository: BaseUserRepository

    @abstractmethod
    async def create(self, attributes: dict[str, Any]): ...

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        join_: set[str, Any] = None,
        order_: dict | None = None,
    ): ...

    @abstractmethod
    async def get_by_id(
        self, id_: int, join_: set[str] | None = None
    ) -> User | None: ...

    @abstractmethod
    async def get_by_filter(
        self,
        field: str,
        value: Any,
        join_: set[str, Any] = None,
        order_: dict | None = None,
    ): ...


@dataclass
class ORMUserService(BaseUserService, BaseOrmService):
    async def create(self, attributes: dict[str, Any]):
        attributes["password"] = PasswordHandler.hash(attributes["password"])
        return await super(BaseUserService, self).create(attributes)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        join_: set[str, Any] = None,
        order_: dict | None = None,
    ): ...

    async def get_by_filter(
        self,
        field: str,
        value: Any,
        join_: set[str, Any] = None,
        order_: dict | None = None,
    ):
        return await super(BaseUserService, self).get_filter(
            field=field, value=value, join_=join_, order_=order_
        )

    async def get_by_id(
        self, id_: int, join_: set[str] | None = None
    ) -> User | None:
        user = await super(BaseUserService, self).get_by_id(
            id_=id_, join_=join_
        )
        if not user:
            raise UserNotFoundException(user_id=id_)
        return user
