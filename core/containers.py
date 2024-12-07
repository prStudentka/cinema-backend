from functools import lru_cache

import punq

from apps.users.models.users import User
from apps.users.repositories.users import BaseUserRepository, ORMUserRepository
from apps.users.services.register import (
    BaseRegisterValidatorService,
    ComposedRegisterValidatorService,
    PasswordIncorrectValidatorService,
    UniqueEmailValidatorService,
)
from apps.users.services.users import BaseUserService, ORMUserService
from apps.users.use_cases.register import RegisterUserUseCase


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_repositories(container: punq.Container) -> None:
    container.register(BaseUserRepository, ORMUserRepository, model_class=User)


def _initialize_services(container: punq.Container) -> None:
    def build_validators() -> BaseRegisterValidatorService:
        return ComposedRegisterValidatorService(
            validators=[
                container.resolve(UniqueEmailValidatorService),
                container.resolve(PasswordIncorrectValidatorService),
            ],
        )

    container.register(UniqueEmailValidatorService)
    container.register(PasswordIncorrectValidatorService)
    container.register(BaseUserService, ORMUserService)
    container.register(BaseRegisterValidatorService, factory=build_validators)


def _initialize_use_cases(container: punq.Container) -> None:
    container.register(RegisterUserUseCase)


def _initialize_container() -> punq.Container:
    container = punq.Container()

    _initialize_repositories(container)
    _initialize_services(container)
    _initialize_use_cases(container)

    return container
