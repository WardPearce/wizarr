import asyncio
from concurrent.futures import ThreadPoolExecutor

from plexapi.myplex import MyPlexAccount, PlexServer

from app.helpers.services.base import ServiceBase, ServiceInviteBase
from app.models.invite import InviteModel


def add_user_blocking(
    invite: InviteModel, token: str, server_api_route: str, server_api_key: str
) -> str:
    plex = PlexServer(server_api_route, server_api_key)

    admin_account = plex.myPlexAccount()
    user_account = MyPlexAccount(token=token)

    admin_account.inviteFriend(
        user=user_account.email,
        server=plex,
        allowSync=invite.plex.allow_sync if invite.plex else False,
        sections=invite.plex.libraries if invite.plex else None,
    )

    user_account.acceptInvite(user_account.email)
    user_account.enableViewStateSync()

    return user_account.email


class PlexInvite(ServiceInviteBase):
    async def add(self, name: str, password: str) -> None:
        invite = await super().add(name, password)

        with ThreadPoolExecutor() as pool:
            plex_email = await asyncio.get_event_loop().run_in_executor(
                pool,
                add_user_blocking,
                invite,
                password,
                str(self._upper.details.url),
                self._upper.details.key,
            )

        if invite.email is None:
            await self._state.mongo.invite.update_one(
                {"_id": self._code}, {"$set": {"email": plex_email}}
            )


class Plex(ServiceBase):
    def invite(self, code: str) -> ServiceInviteBase:
        return PlexInvite(self._state, self, code)
