from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from functools import reduce
from typing import Any, Generic

from sqlalchemy import Select, func
from sqlalchemy.sql.expression import select

from core.database import get_session
from core.generics import ModelType


@dataclass
class BaseRepository(ABC):
    @abstractmethod
    async def create(self, attributes: dict[str, Any] = None): ...

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        join_: set[str] | None = None,
        order_: dict | None = None,
    ): ...

    @abstractmethod
    async def get_by(
        self,
        field: str,
        value: Any,
        join_: set[str] | None = None,
        unique: bool = False,
        order_: dict | None = None,
    ): ...

    @abstractmethod
    async def delete(self, instance: Any) -> None: ...


# ToDO: добавить filter_by и update методы
@dataclass
class BaseORMRepository(BaseRepository, Generic[ModelType]):
    """Базовый класс для репозиториев данных"""

    model_class: ModelType

    async def create(self, attributes: dict[str, Any] = None) -> ModelType:
        """
        Метод для создаения инстанса модели.

        :param attributes: аттрибуты создаваемого инстанса
        :return: возвращает созданный инстанс
        """
        if attributes is None:
            attributes = {}
        model = self.model_class(**attributes)
        async with get_session() as session:
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        join_: set[str] | None = None,
        order_: dict | None = None,
    ) -> Iterable[ModelType]:
        """
        Метод для получения всех инстансов модели.

        :param skip: кол-во записей для пропуска (для пагинации).
        :param limit: кол-во возвращаемых записей
        :param join_: список моделей, к которым необходимо заджоиниться
        :return: список инстансов
        """
        query = self._query(join_)
        query = query.offset(skip).limit(limit)

        if join_ is not None:
            return await self._all_unique(query)

        return await self._all(query)

    async def get_by(
        self,
        field: str,
        value: Any,
        join_: set[str] | None = None,
        unique: bool = False,
        order_: dict | None = None,
    ) -> Iterable[ModelType] | ModelType:
        """
        Метод возвращает инстансы модели, отфильтрованные
        по определенному полю и значению

        :param field: поле для фильтрации.
        :param value: значение для фильтрации.
        :param join_: список джоинов для связи.
        :param unique: нужно ли вернуть одно значение (первое) или их список
        :return: список инстансов или инстанс
        """
        query = self._query(join_)
        query = await self._get_by(query, field, value)

        if join_ is not None:
            return await self._all_unique(query)
        if unique:
            return await self._one(query)

        return await self._all(query)

    async def delete(self, instance: ModelType) -> None:
        """
        Метод для удаления инстанса

        :param instance: инстанс для удаления
        :return: None
        """
        async with get_session() as session:
            await session.delete(instance)

    def _query(
        self,
        join_: set[str] | None = None,
        order_: dict | None = None,
    ) -> Select:
        """
        Метод создает и возвращает query запрос для дальнейшего выполнения.

        :param join_: список моделей для джоина.
        :param order_: сортировка по полям (asc, desc)
        :return: объект query (Select) который используется
        в других методах для доп.фильтрации или запроса
        """
        query = select(self.model_class)
        query = self._maybe_join(query, join_)
        return self._maybe_ordered(query, order_)

    async def _all(self, query: Select) -> Iterable[ModelType]:
        """
        Метод возвращает все инстансы из запроса

        :param query: запрос к бд.
        :return: список инстансов.
        """
        async with get_session() as session:
            query = await session.scalars(query)
            return query.all()

    async def _all_unique(self, query: Select) -> Iterable[ModelType]:
        """
        Метод возвращает уникальные инстансы из запроса

        :param query: запрос к бд.
        :return: список инстансов.
        """
        async with get_session() as session:
            result = await session.execute(query)
            return result.unique().scalars().all()

    async def _first(self, query: Select) -> ModelType | None:
        """
        Метод возвращает первый инстанс из запроса

        :param query: запрос к бд.
        :return: инстанс модели.
        """
        async with get_session() as session:
            query = await session.scalars(query)
            return query.first()

    async def _one_or_none(self, query: Select) -> ModelType | None:
        """
        Метод возвращает первый инстанс из запроса или ничего

        :param query: запрос к бд
        :return: инстанс или None
        """
        async with get_session() as session:
            query = await session.scalars(query)
            return query.one_or_none()

    async def _one(self, query: Select) -> ModelType:
        """
        Метод для получения первого инстанса из запроса.
        Если он не найдет - рейзится NotFound

        :param query: запрос к бд.
        :return: инстанс модели
        """
        async with get_session() as session:
            query = await session.scalars(query)
            return query.one()

    async def _count(self, query: Select) -> int:
        """
        Метод для получения кол-ва инстансов в итоговой выборке

        :param query: запрос к бд
        :return: кол-во инстансов
        """
        async with get_session() as session:
            query = query.subquery()
            query = await session.scalars(
                select(func.count()).select_from(query)
            )
            return query.one()

    async def _sort_by(
        self,
        query: Select,
        sort_by: str,
        order: str | None = "asc",
        model: type[ModelType] | None = None,
        case_insensitive: bool = False,
    ) -> Select:
        """
        Метод для сортировки выборки

        :param query: запрос для сортировки.
        :param sort_by: колонка для сортировки.
        :param order: тип сортировки (asc, desc).
        :param model: модель, по полям которых идет сортировка.
        :param case_insensitive: учитываем ли мы регистр
        или нет при сортировке.
        :return: отсортированный запрос.
        """
        model = model or self.model_class

        order_column = None

        if case_insensitive:
            order_column = func.lower(getattr(model, sort_by))
        else:
            order_column = getattr(model, sort_by)

        if order == "desc":
            return query.order_by(order_column.desc())

        return query.order_by(order_column.asc())

    async def _get_by(self, query: Select, field: str, value: Any) -> Select:
        """
        Метод возвращает запрос, отфильтрованный по указанной колонке.

        :param query: запрос, который нужно отфильтровать.
        :param field: колонка, по которой нужно фильтровать.
        :param value: значение, по которому нужно фильтровать.
        :return: отфильтрованный запрос.
        """
        return query.where(getattr(self.model_class, field) == value)

    def _maybe_join(
        self, query: Select, join_: set[str] | None = None
    ) -> Select:
        """
        Метод возвращает запрос с указанными соединениями (JOIN).

        :param query: запрос, к которому нужно добавить соединения.
        :param join_: соединения, которые нужно добавить.
        :return: запрос с добавленными соединениями.
        """
        if not join_:
            return query

        if not isinstance(join_, set):
            raise TypeError("join_ должен быть множеством")
        # reduce формирует готовый запрос из всех joinoв
        return reduce(self._add_join_to_query, join_, query)

    def _maybe_ordered(
        self, query: Select, order_: dict | None = None
    ) -> Select:
        """
        Метод возвращает запрос, отсортированный по указанной колонке.

        :param query: запрос, который нужно отсортировать.
        :param order_: словарь, указывающий порядок сортировки.
         Должен содержать ключи "asc" (по возрастанию) или "desc" (по убыванию)
         со списками имён полей для сортировки.
        :return: отсортированный запрос.
        """
        if order_:
            if order_["asc"]:
                for order in order_["asc"]:
                    query = query.order_by(
                        getattr(self.model_class, order).asc()
                    )
            else:
                for order in order_["desc"]:
                    query = query.order_by(
                        getattr(self.model_class, order).desc()
                    )

        return query

    def _add_join_to_query(self, query: Select, join_: str) -> Select:
        """
        Метод возвращает запрос с указанным соединением (JOIN).

        :param query: запрос, к которому нужно добавить соединение.
        :param join_: имя соединения, которое нужно добавить.
        :return: запрос с добавленным соединением.
        """
        return getattr(self, "_join_" + join_)(query)
