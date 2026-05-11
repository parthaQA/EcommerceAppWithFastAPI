from pydantic import BaseModel, ConfigDict
from typing import Optional, TypeVar, Generic, List

# 🔹 Base schema (shared fields)
class CategoryBase(BaseModel):
    name: str
    image: str
    description: str


# 🔹 Request schema (for create API)
class CategoryCreateSchema(CategoryBase):
    pass


# 🔹 Response schema (includes DB-generated id)
class CategoryResponseSchema(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# 🔹 Generic response wrapper
T = TypeVar("T")

class ResponseSchema(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
