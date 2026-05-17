from src.products.dtos import ProductSchema
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CartResponseSchema(BaseModel):
    cart_id: str
    location: str

    created_date: datetime
    modified_date: datetime

