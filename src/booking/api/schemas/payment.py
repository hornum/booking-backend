from pydantic import BaseModel


class WebhookPayload(BaseModel):
    session_id: str
    succeeded: bool


class PaymentUrlResponse(BaseModel):
    url: str
