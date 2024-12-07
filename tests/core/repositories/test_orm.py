import random

import pytest
from faker import Faker

from apps.users.models.users import User
from core.repositories.base import BaseORMRepository
from tests.factories.user import UserFactory

faker = Faker(locale="ru_RU")


class TestBaseORMRepository:
    async def test_create(self):
        attrs = await UserFactory()._get_instance_data()
        repository = BaseORMRepository(model_class=User)
        user = await repository.create(attributes=attrs)
        assert user
        assert await repository.get_by(field="id", value=user.id, unique=True)
        for attr, value in attrs.items():
            if hasattr(user, attr):
                assert getattr(user, attr) == value

    async def test_get_all(self, prepare_database):
        instances_count = random.randint(5, 10)
        await UserFactory().create_batch(instances_count=instances_count)
        repository = BaseORMRepository(model_class=User)
        users = await repository.get_all()
        assert users
        assert len(users) == instances_count

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("first_name", faker.first_name()),
            ("last_name", faker.last_name()),
            ("patronymic", faker.middle_name()),
        ],
    )
    async def test_get_by_many(self, field, value, prepare_database):
        instances_count = random.randint(5, 10)
        await UserFactory(kwargs={field: value}).create_batch(
            instances_count=instances_count
        )
        repository = BaseORMRepository(model_class=User)
        users = await repository.get_by(field=field, value=value)
        assert users
        assert len(users) == instances_count
