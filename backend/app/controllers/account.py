from datetime import datetime, timedelta, timezone

from argon2.exceptions import VerificationError
from env import SETTINGS
from helpers.jwt import JWT_COOKIE_AUTH
from litestar import Controller, Request, Response, Router, post
from litestar.exceptions import NotAuthorizedException

from app.helpers.account import Account
from app.models.account import AccountLoginModel, AccountModel
from app.models.session import CreateSessionModel
from app.state import State


class LoginController(Controller):
    path = "/{email:str}"

    @post("/", exclude_from_auth=True)
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


routes = Router("/account", tags=["account"], route_handlers=[LoginController])

__all__ = ["routes"]
