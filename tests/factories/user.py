from faker import Faker
from pydantic import BaseModel, Field

from apps.users.models.users import User
from core.security.password import PasswordHandler
from tests.factories.base import BaseFactory

fake = Faker(locale="ru_RU")


def generate_password():
    return fake.password(length=8, digits=True, upper_case=True)


class UserCreate(BaseModel):
    first_name: str = Field(default_factory=fake.first_name)
    last_name: str = Field(default_factory=fake.last_name)
    patronymic: str = Field(default_factory=fake.middle_name)
    email: str = Field(default_factory=fake.email)
    password: str = Field(default_factory=generate_password)


class UserFactory(BaseFactory[User, UserCreate]):
    model_class = User
    schema = UserCreate

    async def _get_instance_data(self) -> dict:
        instance_data = await super()._get_instance_data()
        instance_data["password"] = PasswordHandler.hash(
            instance_data["password"]
        )
        return instance_data
