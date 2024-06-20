from bson import Int64, ObjectId
from pydantic import BaseModel, ConfigDict, Field

TYPE_ENCODERS = {
    ObjectId: lambda v: str(v),
    Int64: lambda v: int(v),
}


class CustomJsonEncoder(BaseModel):
    model_config = ConfigDict(
        json_encoders=TYPE_ENCODERS,  # type: ignore
        arbitrary_types_allowed=True,
    )
