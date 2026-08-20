from pydantic import BaseModel


class InventoryRecord(BaseModel):
    circuit_id: str
    address: str
    status: str
