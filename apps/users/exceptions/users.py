from dataclasses import dataclass

from core.exceptions import NotFoundException


@dataclass
class UserNotFoundException(NotFoundException):
    user_id: int = None

    @property
    def message(self):
        return f"Пользователь с айди {self.user_id} не найден"
