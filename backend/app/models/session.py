from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.customs import CustomJsonEncoder


class CreateSessionModel(CustomJsonEncoder):
    expires: datetime
    created: datetime
    device: Optional[str] = None
    email: str


class SessionModel(CreateSessionModel):
    id: ObjectId = Field(..., alias="_id")
