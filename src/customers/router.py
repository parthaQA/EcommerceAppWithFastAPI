from typing import List
from fastapi import APIRouter, Depends, status, Request
from src.customers.controller import CustomerController
from src.customers.dtos import CustomerSchema, CustomerResponseSchema, CustomerRegisterSchema, \
    CustomerRegistrationResponseSchema, CustomerLoginSchema
from src.utils.db import get_db
from sqlalchemy.orm import Session

customer_routes = APIRouter(prefix="/customers")


@customer_routes.post(path="/create", response_model=CustomerResponseSchema,
                      status_code=status.HTTP_201_CREATED, summary="Create a new customer")
def create_customer(body: CustomerSchema, db: Session=Depends(get_db)):
    return CustomerController().create_customer(body, db)


@customer_routes.get(path="/all", response_model=List[CustomerResponseSchema], status_code=status.HTTP_200_OK, summary="Get all customers")
def get_all_customers(db: Session=Depends(get_db)):
    return CustomerController().get_all_customers(db)

@customer_routes.get(path="/is_auth", status_code=status.HTTP_200_OK, summary="authenticate a customer")
def is_authenticated(request: Request):
    return CustomerController().is_authenticated(request)

@customer_routes.get(path="/{customer_id}", response_model=CustomerResponseSchema, status_code=status.HTTP_200_OK,  summary="Get customer by id")
def get_customer(customer_id: str, db: Session=Depends(get_db)):
    return CustomerController().get_customer_by_id(customer_id=customer_id, db=db)


@customer_routes.post(path="/register", response_model=CustomerRegistrationResponseSchema, status_code=status.HTTP_200_OK, summary="Register a new customer")
def register_customer(body: CustomerRegisterSchema, db: Session=Depends(get_db)):
    return CustomerController().register_customer(body, db)


@customer_routes.post(path="/login", status_code=status.HTTP_200_OK, summary="Login a customer")
async def customer_login(request: Request, body: CustomerLoginSchema, db: Session=Depends(get_db)):
    return await CustomerController().customer_login(body, db, request)

