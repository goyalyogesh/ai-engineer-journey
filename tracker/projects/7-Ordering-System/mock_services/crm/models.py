from pydantic import BaseModel


class OrderRecord(BaseModel):
    order_id: str
    customer_id: str
    service_type: str
    address: str
    status: str
    created_at: str
