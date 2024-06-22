from datetime import datetime, timedelta, timezone
from typing import Any, cast

from argon2.exceptions import VerificationError
from bson import ObjectId
from litestar import Controller, Request, Response, Router, delete, post
from litestar.contrib.jwt import Token
from litestar.exceptions import NotAuthorizedException

from app.env import SETTINGS
from app.helpers.account import Account
from app.helpers.jwt import JWT_COOKIE_AUTH
from app.models.account import AccountLoginModel, AccountModel
from app.models.session import CreateSessionModel
from app.state import State


class LoginController(Controller):
    path = "/{email:str}"

    @post("/login", exclude_auth=True)
    async def login(
        self, request: Request, email: str, state: State, data: AccountLoginModel
    ) -> Response[AccountModel]:
        account = Account(state, email)

        try:
            await account.validate_password(data.password)
        except VerificationError:
            raise NotAuthorizedException()

        details = await account.get()

        now = datetime.now(tz=timezone.utc)
        expires = now + timedelta(seconds=SETTINGS.jwt.expires_in)

        session = await state.mongo.session.insert_one(
            CreateSessionModel(
                email=email,
                expires=expires,
                created=now,
                device=request.headers.get("User-Agent", None),
            ).model_dump()
        )

        return JWT_COOKIE_AUTH.login(
            identifier=details.email,
            response_body=details,
            token_unique_jwt_id=str(session.inserted_id),
        )


@delete("/logout")
async def logout(request: Request[str, Token, Any], state: State) -> None:
    request.cookies.pop(JWT_COOKIE_AUTH.key)

    search = {"_id": ObjectId(request.auth.jti), "email": request.user}

    await state.mongo.session.delete_one(search)
    await request.app.stores.get("auth_cache").delete(cast(str, request.auth.jti))


routes = Router("/account", tags=["account"], route_handlers=[LoginController, logout])

__all__ = ["routes"]
