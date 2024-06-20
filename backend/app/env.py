import secrets

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class MongoDB(BaseModel):
    host: str = "localhost"
    port: int = 27017
    collection: str = "wizarr_v5"


class JWT(BaseModel):
    secret: str = Field(default=secrets.token_urlsafe(), min_length=32)
    expires_in: int = 2678400


class Settings(BaseSettings):
    mongo: MongoDB = MongoDB()

    backend_url: str
    frontend_url: str

    debug: bool = False

    jwt: JWT = JWT()

    model_config = {"env_prefix": "wizarr_"}


SETTINGS = Settings()  # type: ignore
