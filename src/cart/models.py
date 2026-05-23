from pydantic import ConfigDict
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Boolean
from src.utils.db import BASE
from datetime import datetime, timedelta, timezone


class CartModel(BASE):
    __tablename__ = "cart"

    cart_id = Column[str](String, primary_key=True, index=True, unique=True, nullable=False)
    location = Column[str](String, nullable=False)
    customer_id = Column[str](String, ForeignKey("customers.id"))
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    status = Column(String, default="ACTIVE")

    expires_at = Column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc) + timedelta(days=7)
)

    model_config = ConfigDict(from_attributes=True)



class CartItemModel(BASE):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    cart_id = Column(String, ForeignKey("cart.cart_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer, default=1)
    is_checkout = Column(Boolean, default=False, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)