from litestar import Router

from app.controllers import account, invites, services, session

routes = Router(
    "/api/v5",
    route_handlers=[services.routes, account.routes, invites.routes, session.routes],
)

__all__ = ["routes"]
