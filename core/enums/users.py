from enum import Enum


class RoleKindEnum(Enum):
    CLIENT = (1, "Клиент")
    EMPLOYEE = (2, "Сотрудник")
    ADMIN = (3, "Администратор")
