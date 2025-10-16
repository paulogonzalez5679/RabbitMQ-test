# orders_service/models.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    note: Optional[str] = None

class OrderInDB(OrderCreate):
    id: str
    created_at: datetime

class OrderResponse(BaseModel):
    id: str
    customer_name: str
    product_id: str
    quantity: int
    created_at: datetime
