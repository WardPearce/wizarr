from helpers.services.base import ServiceBase, ServiceInviteBase
from models.invite import InviteModel


class EmbyInvite(ServiceInviteBase):
    async def add(self, name: str, password: str) -> None:
        invite = await super().add(name, password)

        created_user = await (
            await self._upper.request("/Users/New", "POST", json={"Name": name})
        ).json()

        user_policy: dict[str, bool | str | int | list[str]] = {
            "EnableLiveTvManagement": False,
            "AuthenticationProviderId": "Emby.Server.Implementations.Library.DefaultAuthenticationProvider",
        }

        if invite.emby and invite.emby.libraries:
            user_policy["EnableAllFolders"] = False
            user_policy["EnabledFolders"] = invite.emby.libraries
        else:
            user_policy["EnableAllFolders"] = True

        if invite.sessions is not None:
            user_policy["SimultaneousStreamLimit"] = invite.sessions

        if invite.hidden is not None:
            user_policy["IsHiddenRemotely"] = invite.hidden

        if invite.live_tv is not None:
            user_policy["EnableLiveTvAccess"] = invite.live_tv
        else:
            user_policy["EnableLiveTvAccess"] = False

        await self._upper.request(
            f"/Users/{created_user['Id']}/Policy",
            "POST",
            json={**created_user["Policy"], **user_policy},
        )

        await self._upper.request(
            f"/Users/{created_user['Id']}/Password", "POST", json={"NewPw", password}
        )


class Emby(ServiceBase):
    def invite(self, code: str) -> EmbyInvite:
        return EmbyInvite(self._state, self, code)
