from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from src.cart.dtos import CartResponseSchema, CartItemSchema, CartProductsResponseSchema, CartProductSchema
from src.cart.models import CartModel, CartItemModel
from src.products.dtos import ProductSchema
from src.utils.helper import Helper
from src.customers.controller import CustomerController
from src.customers.models import CustomerModel
from datetime import datetime, timedelta, timezone
from src.products.models import ProductModel



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
        #  # Check existing active cart
        # existing_cart = db.query(CartModel).filter(
        # CartModel.customer_id == customer_id,
        # CartModel.status == "ACTIVE",
        # CartModel.expires_at > datetime.now(timezone.utc)
        # ).first()

        # if existing_cart:
        #     return {
        #     "success": True,
        #     "data": existing_cart,
        #     "message": "Existing cart found"
        # }
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

    
    @staticmethod
    def add_product_to_cart(request: Request, cart_id: str, body: CartItemSchema, db: Session):

        customer_authenticated = CustomerController.is_authenticated(request)

        if customer_authenticated["message"] != "Authenticated":
            return {
                "success": False,
                "data": [],
                "message": "Customer not authenticated"
            }
        is_cart_exists = db.query(CartModel).filter(CartModel.cart_id== cart_id).first()
        if not is_cart_exists:
            raise HTTPException(status_code=404, detail= "cart id not found")

        is_product_exist = db.query(ProductModel).filter(ProductModel.product_id==body.product_id).first()

        if not is_product_exist:
            raise HTTPException(status_code=404, detail="product id does not exist")
        
        if is_product_exist.product_quantity < body.quantity:
            raise HTTPException(
            status_code=400,
            detail="quantity not available"
            )
    
        
        cart_products = CartItemModel(
            cart_id=cart_id,
            product_id=body.product_id,
            quantity=body.quantity,
            is_checkout=body.is_checkout,
        )
        db.add(cart_products)
        db.commit()
        db.refresh(cart_products)

        product_response = ProductSchema(
        product_name=is_product_exist.product_name,
        product_description=is_product_exist.product_description,
        product_price=is_product_exist.product_price,
        product_quantity=body.quantity,
        category_id=is_product_exist.category_id
    )
        cart_product = CartProductSchema(
        product_id=is_product_exist.product_id,
        product_details=[product_response]
    )

        return {
            "success": True,
            "data": CartProductsResponseSchema(cart_id=cart_id,
            cart_products=cart_product
            ),
            "message": "product is added to cart"
        }


       