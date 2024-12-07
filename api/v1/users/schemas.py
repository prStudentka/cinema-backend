from dataclasses import field

from pydantic import BaseModel, EmailStr


class UserRegisterSchema(BaseModel):
    first_name: str
    last_name: str
    patronymic: str = None
    password: str
    email: EmailStr


class UserRegisterCompleteSchema(BaseModel):
    id: int
    status: str = field(default="Вы успешно зарегистрировались")
