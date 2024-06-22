from typing import Optional, cast

from bson.objectid import ObjectId
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import Token
from litestar.security.jwt import JWTCookieAuth

from app.env import SETTINGS
from app.models.account import AccountModel
from app.state import State


async def retrieve_account_handler(
    token: "Token", connection: ASGIConnection
) -> Optional[str]:
    jti = cast(str, token.jti)

    cache = connection.app.stores.get("auth_cache")
    whitelisted = await cache.get(jti)

    if whitelisted is None:
        state = cast("State", connection.scope["app"].state)

        if await state.mongo.session.count_documents({"_id": ObjectId(jti)}) > 0:
            await cache.set(jti, "true", 360)
            return token.sub
    elif whitelisted == b"true":
        return token.sub


JWT_COOKIE_AUTH = JWTCookieAuth[AccountModel](
    retrieve_user_handler=retrieve_account_handler,
    token_secret=SETTINGS.jwt.secret,
    exclude=["/schema"],
    exclude_opt_key="exclude_auth",
)
