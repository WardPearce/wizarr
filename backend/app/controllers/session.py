from typing import Any, List

from bson import ObjectId
from litestar import Request, Router, delete, get
from litestar.contrib.jwt import Token

from app.models.session import SessionModel
from app.state import State


@get(path="/", description="List active sessions", tags=["session"])
async def get_sessions(
    request: Request[str, Token, Any], state: "State"
) -> List[SessionModel]:
    sessions = []
    async for session in state.mongo.session.find({"email": request.user}).sort(
        "created", -1
    ):
        sessions.append(SessionModel(**session))

    return sessions


@delete(path="/{session_id:str}", description="Invalidate a session", tags=["session"])
async def invalidate_session(
    request: Request[str, Token, Any], state: "State", session_id: str
) -> None:
    search = {"_id": ObjectId(session_id), "email": request.user}

    if await state.mongo.session.count_documents(search) > 0:
        await state.mongo.session.delete_one(search)
        await request.app.stores.get("auth_cache").delete(session_id)


routes = Router(path="/session", route_handlers=[get_sessions, invalidate_session])
