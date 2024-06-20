from typing import Optional, cast

from bson.objectid import ObjectId
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import Token

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
