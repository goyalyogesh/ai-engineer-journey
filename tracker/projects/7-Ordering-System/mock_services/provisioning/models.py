from pydantic import BaseModel


class ProvisioningRecord(BaseModel):
    order_id: str
    status: str
    error_code: str | None
    circuit_id: str | None
    updated_at: str
