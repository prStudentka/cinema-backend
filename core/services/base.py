from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from core.generics import ModelType
from core.repositories import BaseRepository


@dataclass
class BaseService(ABC):
    @abstractmethod
    async def create(self, attributes: dict[str, Any] = None): ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100): ...

    @abstractmethod
    async def get_filter(
        self,
        field: str,
        value: Any,
        join_: set[str, Any] = None,
        order_: dict | None = None,
    ): ...

    @abstractmethod
    async def delete(self, instance: Any) -> None: ...

    @abstractmethod
    async def get_by_id(self, id_: int): ...


# ToDo добавить другие базовые crud методы
@dataclass
class BaseOrmService(BaseService):
    """Базовый класс сервисов для работы с данными"""

    repository: BaseRepository

    async def create(self, attributes: dict[str, Any] = None) -> ModelType:
        return await self.repository.create(attributes)

    async def get_all(self, skip: int = 0, limit: int = 100): ...

    async def get_filter(
        self,
        field: str,
        value: Any,
        join_: set[str, Any] = None,
        order_: dict | None = None,
    ) -> Iterable[ModelType] | list[None]:
        return await self.repository.get_by(
            field=field, value=value, join_=join_, order_=order_
        )

    async def delete(self, instance: Any) -> None: ...

    async def get_by_id(
        self, id_: int, join_: set[str] | None = None
    ) -> ModelType:
        """
        Метод ищет инстанс в модели по айди

        :param id_: айди для поиска
        :param join_: соединения, которые нужно добавить
        :return: найденный инстанс
        """

        return await self.repository.get_by(
            field="id", value=id_, join_=join_, unique=True
        )
