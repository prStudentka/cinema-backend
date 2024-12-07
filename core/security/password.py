from passlib.context import CryptContext


class PasswordHandler:
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
    )

    @classmethod
    def hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def verify(cls, hashed_password: str, password_to_verify: str) -> bool:
        return cls.pwd_context.verify(password_to_verify, hashed_password)
