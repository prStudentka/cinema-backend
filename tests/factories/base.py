from collections.abc import Iterable
from typing import Generic, TypeVar

from core.database import get_session
from core.generics import ModelType

InstanceSchemaType = TypeVar("InstanceSchemaType")


class BaseFactory(Generic[ModelType, InstanceSchemaType]):
    """
    Базовый класс для генерации инстансов моделей для тестов
    Для использования отнаследуйтесь от него и определите model_class и schema
    По необходимости - переопределить/расширить _get_instance_data

    :param model_class: Модель
    :param schema: Схема, которая создает фейковые данные
    """

    model_class: ModelType
    schema: InstanceSchemaType

    def __init__(self, kwargs: dict = None):
        self.kwargs = kwargs

    async def create(self, **kwargs) -> type[ModelType]:
        async with get_session() as session:
            instance_data = await self._get_instance_data()
            instance = self.model_class(**instance_data)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def create_batch(self, instances_count: int) -> Iterable[ModelType]:
        instances = []
        async with get_session() as session:
            for _i in range(instances_count):
                instance_data = await self._get_instance_data()
                instance = self.model_class(**instance_data)
                session.add(instance)
                instances.append(instance)
            await session.commit()
        return instances

    async def _get_instance_data(self) -> dict:
        instance_data = await self.__get_fake_instance_data()
        if self.kwargs:
            for attr, value in self.kwargs.items():
                if attr in instance_data:
                    instance_data[attr] = value
        return instance_data

    async def __get_fake_instance_data(self) -> dict:
        return self.schema().dict()
