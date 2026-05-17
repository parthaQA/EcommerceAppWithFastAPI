from fastapi import APIRouter, Depends, status, Query, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from src.cart.controller import CartController
from src.cart.dtos import CartResponseSchema
from src.utils.db import get_db


cart_routes = APIRouter(prefix="/cart")


@cart_routes.get(path="/get", status_code=status.HTTP_200_OK, summary="Get a new cart")
def get_cart(request: Request, customer_id: Annotated[str, Query(...)], location: Annotated[str, Query(...)],db: Session = Depends(get_db)):
   
    return CartController.get_cart(request,customer_id,location, db)