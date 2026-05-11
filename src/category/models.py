from sqlalchemy import Column, String, DateTime, Integer, Sequence
from sqlalchemy.orm import relationship

from src.utils.db import BASE
from datetime import datetime

class CategoryModel(BASE):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    name = Column(String, unique=True, nullable=False, index=True)

    category_code = Column(
        Integer,
        Sequence('category_code_seq', start=1000, increment=1),
        unique=True,
        index=True,
        nullable=False
    )

    image = Column(String)
    description = Column(String)

    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    products = relationship("ProductModel", back_populates="category")