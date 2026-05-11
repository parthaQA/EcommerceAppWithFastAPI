from datetime import datetime
from pydantic import BaseModel, field_serializer


class CustomerSchema(BaseModel):
    name: str
    email: str
    address: str
    gender: str
    mobile: int
    pincode: int
    is_active: bool = False


class CustomerResponseSchema(BaseModel):
    id : str
    name: str
    gender: str
    mobile: int


class CustomerRegisterSchema(BaseModel):
    mobile: int
    password: str


class CustomerRegistrationResponseSchema(BaseModel):
    id: int
    mobile: int


class CustomerLoginSchema(BaseModel):
    mobile: int
    password: str