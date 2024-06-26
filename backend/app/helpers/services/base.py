from typing import Literal

from aiohttp.client import ClientResponse
from argon2.exceptions import VerificationError

from app.const import ARGON
from app.exceptions import InvalidInviteCode, WeakPassword
from app.helpers.misc import check_password
from app.models.invite import InviteModel
from app.models.services.base import ServiceApiModel
from app.state import State


class ServiceInviteBase:
    def __init__(self, state: State, upper: "ServiceBase", code: str) -> None:
        self._state = state
        self._upper = upper
        self._code = code

    async def add(self, name: str | None, password: str) -> InviteModel:
        try:
            invite = await self.validate()
        except InvalidInviteCode:
            raise

        try:
            check_password(password)
        except WeakPassword:
            raise

        return invite

    async def delete(self) -> None:
        await self._state.mongo.delete_one({"_id": self._code})

    async def get(self) -> InviteModel:
        result = await self._state.mongo.invite.find_one({"_id", self._code})
        if not result:
            raise InvalidInviteCode()

        return InviteModel(**result)

    async def validate(self) -> InviteModel:
        invite = await self.get()

        try:
            # Timing attacks
            ARGON.verify(ARGON.hash(invite.id), self._code)
        except VerificationError:
            raise InvalidInviteCode()

        return invite


class ServiceBase:
    def __init__(self, state: State, service: ServiceApiModel) -> None:
        self._state = state
        self._service = service

    @property
    def details(self) -> ServiceApiModel:
        return self._service

    def invite(self, code: str) -> ServiceInviteBase: ...

    async def request(
        self,
        path: str,
        method: Literal["POST"] | Literal["GET"] | Literal["DELETE"] | Literal["PATCH"],
        **kwargs,
    ) -> ClientResponse:
        url = str(self._service.url)
        if url.endswith("/"):
            url = url.removesuffix("/")

        if "headers" not in kwargs:
            kwargs["headers"] = {}

        if self._service.type == "emby":
            kwargs["headers"]["Accept"] = 'application/json, profile="PascalCase"'

        kwargs["headers"][
            "X-Emby-Token" if self._service.type != "plex" else "X-Plex-Token"
        ] = self._service.key

        resp = await self._state.aiohttp.request(
            method=method, url=f"{self._service.url}/{path}", **kwargs
        )

        resp.raise_for_status()

        return resp

    async def policy(self) -> None: ...
