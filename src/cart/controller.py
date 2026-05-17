from sqlalchemy.orm import Session
from fastapi import Request
from src.cart.dtos import CartResponseSchema
from src.cart.models import CartModel
from src.utils.helper import Helper
from src.customers.controller import CustomerController
from src.customers.models import CustomerModel
from datetime import datetime, timedelta, timezone


class CartController:

    @staticmethod
    def get_cart(request: Request, customer_id: str, location: str, db: Session):
        customer_exists = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if not customer_exists:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer_authenticated = CustomerController.is_authenticated(request)

        if customer_authenticated["message"] != "Authenticated":
            return {
                "success": False,
                "data": [],
                "message": "Customer not authenticated"
            }
         # Check existing active cart
        existing_cart = db.query(CartModel).filter(
        CartModel.customer_id == customer_id,
        CartModel.status == "ACTIVE",
        CartModel.expires_at > datetime.now(timezone.utc)
        ).first()

        if existing_cart:
            return {
            "success": True,
            "data": existing_cart,
            "message": "Existing cart found"
        }
        cart_id = Helper.generate_cart_id()
        cart=CartModel(cart_id=cart_id, location=location, customer_id=customer_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

        return {
            "success": True,
            "data": CartResponseSchema(cart_id=cart.cart_id, location=cart.location, created_date=cart.created_date,
            modified_date=cart.modified_date),
            "message": "Cart retrieved successfully"
            }
       