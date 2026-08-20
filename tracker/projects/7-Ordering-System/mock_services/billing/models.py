from pydantic import BaseModel


class BillingRecord(BaseModel):
    customer_id: str
    payment_status: str
    hold_active: bool
    hold_reason: str | None
    plan: str
