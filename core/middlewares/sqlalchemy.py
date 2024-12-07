from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

from core.database.session import (
    reset_session_context,
    session,
    set_session_context,
)


class SQLAlchemyMiddleware:
    """Middleware для управления сессиями БД.
    Создаёт новую сессию для каждого нового запроса
    для обеспечения I из ACID - изоляции запросов"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        session_id = str(uuid4())
        context = set_session_context(session_id=session_id)

        try:
            await self.app(scope, receive, send)
        except Exception as exception:
            await session.rollback()
            raise exception
        finally:
            await session.remove()
            reset_session_context(context=context)
