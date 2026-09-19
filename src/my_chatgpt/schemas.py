from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)


class SendMessageResponse(BaseModel):
    response: str
