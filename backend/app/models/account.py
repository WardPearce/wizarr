from datetime import datetime

from pydantic import BaseModel


class AccountLoginModel(BaseModel):
    password: str


class AccountModel(BaseModel):
    password_hash: str
    email: str
    created: datetime
    scopes: list[str] = []
    last_login: datetime | None = None
    services: list[str] = []


class AccountUpdateModel(BaseModel):
    email: str | None = None
