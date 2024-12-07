from fastapi import Depends
from fastapi.requests import Request
from fastapi.routing import APIRouter

from api.v1.users.schemas import UserRegisterCompleteSchema, UserRegisterSchema
from apps.users.use_cases.register import RegisterUserUseCase
from core.containers import get_container
from core.schemas.responses.api_response import ApiResponse

router = APIRouter()


@router.post("/register")
async def user_register_handler(
    request: Request,
    user_data: UserRegisterSchema,
    container=Depends(get_container),  # noqa: B008
) -> ApiResponse[UserRegisterCompleteSchema]:
    use_case: RegisterUserUseCase = container.resolve(RegisterUserUseCase)
    user_data = user_data.dict()
    user = await use_case.execute(user_data=user_data)
    return ApiResponse(data=UserRegisterCompleteSchema(id=user.id))
