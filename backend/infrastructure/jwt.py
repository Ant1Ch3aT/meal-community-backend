from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, Callable, Coroutine, Optional, cast

from jwt import decode, encode
from sanic import Unauthorized

from backend.infrastructure.sanic import BackendRequest


def jwt_encode(payload: dict[str, Any], secret: str, exp: int):
    return encode(
        {**payload, "exp": datetime.now(UTC) + timedelta(seconds=exp)},
        secret,
        algorithm="HS256",
    )


def jwt_decode(token: str, secret: str):
    return decode(
        token,
        secret,
        algorithms=["HS256"],
    )


def require_auth(f: Callable[..., Any]) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(f)
    async def decorated_function(request: BackendRequest, *args: Any, **kwargs: Any):
        authorization = cast(Optional[str], request.headers.get("Authorization"))
        if not authorization:
            raise Unauthorized("Authorization header is missing.")

        prefix, token = authorization.split(" ")

        if prefix != "Bearer":
            raise Unauthorized("Prefix not Bearer.")

        try:
            result = request.app.ctx.jwt_decode(token)
        except Exception:
            raise Unauthorized("Invalid token.")

        return await f(request, result["user_id"], *args, **kwargs)

    return decorated_function
