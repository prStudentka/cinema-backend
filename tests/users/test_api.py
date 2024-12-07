import pytest
from httpx import AsyncClient

from apps.users.services.users import BaseUserService
from tests.factories.user import UserFactory


class TestUserApi:
    @staticmethod
    def get_register_url(**kwargs):
        return "api/v1/users/register"

    async def test_user_register(self, client: AsyncClient, faker, container):
        payload = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "password": faker.password(length=8, digits=True, upper_case=True),
            "email": faker.email(),
        }

        response = await client.post(self.get_register_url(), json=payload)
        assert response.status_code == 200
        user_service = container.resolve(BaseUserService)
        user = await user_service.get_by_id(response.json()["data"]["id"])
        assert user.id == response.json()["data"]["id"]
        for attr, value in payload.items():
            if hasattr(user, attr) and attr != "password":
                assert getattr(user, attr) == value

    async def test_user_register_with_exist_email(
        self, client: AsyncClient, faker, container
    ):
        user = await UserFactory().create()
        payload = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "password": faker.password(length=8, digits=True, upper_case=True),
            "email": user.email,
        }
        response = await client.post(self.get_register_url(), json=payload)
        assert response.status_code == 409
        user_service = container.resolve(BaseUserService)
        user = await user_service.get_by_filter(
            field="first_name", value=payload["last_name"]
        )
        assert not user

    @pytest.mark.asyncio
    async def test_user_register_with_bad_password(
        self, client: AsyncClient, faker, container
    ):
        payload = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "password": "simplepass",
            "email": faker.email(),
        }
        response = await client.post(self.get_register_url(), json=payload)
        assert response.status_code == 400
        user_service = container.resolve(BaseUserService)
        user = await user_service.get_by_filter(
            field="email", value=payload["email"]
        )
        assert not user
