from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Annotated

from src.utils.db import get_db
from src.category.controller import CategoryController
from src.category.dtos import (
    CategoryCreateSchema,
    CategoryResponseSchema,
    ResponseSchema
)

category_routes = APIRouter(prefix="/category")


# 🔹 Create Category
@category_routes.post(
    "/create",
    response_model=ResponseSchema[CategoryResponseSchema],
    status_code=status.HTTP_201_CREATED
)
def create_category(body: CategoryCreateSchema, db: Session = Depends(get_db)):
    return CategoryController.create_categories(body, db)


# 🔹 Get All Categories
@category_routes.get(
    "/all",
    response_model=ResponseSchema[List[CategoryResponseSchema]],
    status_code=status.HTTP_200_OK
)
def get_all_categories(db: Session = Depends(get_db)):
    return CategoryController.get_all_categories(db)


@category_routes.get(
    "/{id}", response_model=ResponseSchema[List[CategoryResponseSchema]],
    status_code=status.HTTP_200_OK
)
def get_category_by_id(id: int, category_code : Annotated[ int, Query(...)], db: Session = Depends(get_db)):
    return CategoryController.get_cateogry_by_id(id, category_code, db)

