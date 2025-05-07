from sanic import BadRequest, json
from sanic.blueprints import Blueprint
from sanic_ext import validate

from backend.application.dtos.user import CreateUserDTO, LoginUserDTO
from backend.application.use_cases.create.refresh_token import CreateRefreshTokenUseCase
from backend.application.use_cases.create.user import CreateUserUseCase
from backend.application.use_cases.delete.refresh_token import DeleteRefreshTokenUseCase
from backend.application.use_cases.get.refresh_token import GetRefreshTokenUseCase
from backend.application.use_cases.get.user import (
    GetUserByIDUseCase,
    GetUserIDByEmailWithPassword,
)
from backend.application.use_cases.update.refresh_token import (
    UpdateRefreshTokenTTLUseCase,
)
from backend.infrastructure.jwt import require_auth
from backend.infrastructure.sanic import BackendRequest

user = Blueprint("user_endpoint", url_prefix="/user")


@user.post("/register")
@validate(json=CreateUserDTO, body_argument="create_user_dto")
async def register_user(
    request: BackendRequest,
    create_user_dto: CreateUserDTO,
):
    user = await CreateUserUseCase(request.app.ctx.user_repository).execute(
        create_user_dto
    )
    user_id = await GetUserIDByEmailWithPassword(
        request.app.ctx.user_repository
    ).execute(user.email, user.password)

    refresh_token = await CreateRefreshTokenUseCase(
        request.app.ctx.refresh_token_repository
    ).execute(user_id)

    response = json(
        {
            "access_token": request.app.ctx.jwt_encode({"user_id": user_id}),
        }
    )

    response.add_cookie(
        "refresh_token",
        refresh_token.value,
        max_age=60 * 60 * 24 * 7,  # 7 days
        samesite="strict",
        secure=False,
        httponly=True,
    )

    return response


@user.post("/login")
@validate(json=LoginUserDTO, body_argument="login_user_dto")
async def login_user(request: BackendRequest, login_user_dto: LoginUserDTO):
    email = login_user_dto.email
    password = login_user_dto.password

    if not email or not password:
        raise BadRequest("Email or Password is missing.")

    user_id = await GetUserIDByEmailWithPassword(
        request.app.ctx.user_repository
    ).execute(email, password)

    refresh_token = await CreateRefreshTokenUseCase(
        request.app.ctx.refresh_token_repository
    ).execute(user_id)

    response = json(
        {
            "access_token": request.app.ctx.jwt_encode({"user_id": user_id}),
        }
    )

    response.add_cookie(
        "refresh_token",
        refresh_token.value,
        max_age=60 * 60 * 24 * 7,  # 7 days
        samesite="strict",
        secure=False,
        httponly=True,
    )

    return response


@user.get("/me")
@require_auth
async def get_user(request: BackendRequest, user_id: int):
    user = await GetUserByIDUseCase(request.app.ctx.user_repository).execute(user_id)
    return json(user.to_dict())


@user.post("/check")
@require_auth
async def is_valid_user(request: BackendRequest, user_id: int):
    client_refresh_token_value = request.cookies.get("refresh_token")
    if not client_refresh_token_value:
        raise BadRequest("Refresh token is missing.")

    exist_refresh_token = await GetRefreshTokenUseCase(
        request.app.ctx.refresh_token_repository
    ).execute(client_refresh_token_value)

    await UpdateRefreshTokenTTLUseCase(
        request.app.ctx.refresh_token_repository
    ).execute(exist_refresh_token.value)

    return json({"message": "Valid user."})


@user.post("/refresh")
async def refresh_token(request: BackendRequest):
    client_refresh_token_value = request.cookies.get("refresh_token")
    if not client_refresh_token_value:
        raise BadRequest("Refresh token is missing.")

    exist_refresh_token = await GetRefreshTokenUseCase(
        request.app.ctx.refresh_token_repository
    ).execute(client_refresh_token_value)

    await DeleteRefreshTokenUseCase(request.app.ctx.refresh_token_repository).execute(
        exist_refresh_token.value
    )

    new_refresh_token = await CreateRefreshTokenUseCase(
        request.app.ctx.refresh_token_repository
    ).execute(exist_refresh_token.user_id)

    response = json(
        {
            "access_token": request.app.ctx.jwt_encode(
                {"user_id": new_refresh_token.user_id}
            ),
        }
    )
    response.add_cookie(
        "refresh_token",
        new_refresh_token.value,
        max_age=60 * 60 * 24 * 7,  # 7 days
        samesite="strict",
        secure=False,
        httponly=True,
    )
    return response


@user.get("/logout")
async def logout_user(request: BackendRequest):
    client_refresh_token_value = request.cookies.get("refresh_token")
    if not client_refresh_token_value:
        raise BadRequest("Refresh token is missing.")

    exist_refresh_token = await GetRefreshTokenUseCase(
        request.app.ctx.refresh_token_repository
    ).execute(client_refresh_token_value)

    await DeleteRefreshTokenUseCase(request.app.ctx.refresh_token_repository).execute(
        exist_refresh_token.value
    )

    response = json({"message": "Logout successful"})
    response.delete_cookie("refresh_token")
    return response


@user.post("/modify")
async def modify_user(request: BackendRequest): ...
