from pydantic import BaseModel


class LenderRejectCreate(BaseModel):

    reason: str