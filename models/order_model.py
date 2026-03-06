"""
Order Model – Pydantic schemas for order request and response.
"""

from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class OrderRequest(BaseModel):
    name:    str = Field(..., min_length=2, max_length=100, description="Customer full name")
    phone:   str = Field(..., min_length=10, max_length=15, description="Mobile number")
    address: str = Field(..., min_length=5, max_length=500, description="Delivery address")
    variant: Literal["11g", "33g"] = Field(..., description="Yantra variant (11g or 33g)")


class OrderResponse(BaseModel):
    message:    str
    order_id:   str
    variant:    str
    price:      str
    created_at: str


class StoredOrder(BaseModel):
    order_id:   str
    name:       str
    phone:      str
    address:    str
    variant:    str
    price:      str
    status:     str = "pending"
    created_at: str
