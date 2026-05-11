from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from src.category.models import CategoryModel
from src.category.dtos import (
    CategoryCreateSchema,
    CategoryResponseSchema,
    ResponseSchema
)

class CategoryController:

    @staticmethod
    def create_categories(body: CategoryCreateSchema, db: Session):
        try:
            # 🔍 Check duplicate (case-insensitive)
            existing_category = db.query(CategoryModel).filter(
                func.lower(CategoryModel.name) == body.name.lower()
            ).first()

            if existing_category:
                return ResponseSchema(
                    success=False,
                    data=None,
                    message="Category already exists"
                )

            category = CategoryModel(
                name=body.name.strip(),
                image=body.image,
                description=body.description
            )

            db.add(category)
            db.commit()
            db.refresh(category)

            return ResponseSchema(
                success=True,
                data=CategoryResponseSchema.model_validate(category),
                message="Category created successfully"
            )

        except Exception as e:
            return ResponseSchema(
                success=False,
                data=None,
                message=str(e)
            )

    @staticmethod
    def get_all_categories(db: Session):
        try:
            categories = db.query(CategoryModel).all()

            return ResponseSchema(
                success=True,
                data=[CategoryResponseSchema.model_validate(c) for c in categories],  # ✅ FIX
                message="All categories retrieved successfully" if categories else "No categories found"
            )

        except Exception as e:
            return ResponseSchema(
                success=False,
                data=None,
                message=str(e)
            )

    @staticmethod
    def get_cateogry_by_id(id, category_code, db: Session):
        category_id = db.query(CategoryModel).filter(CategoryModel.id == id).first()
        cat_code = db.query(CategoryModel).filter(CategoryModel.category_code == category_code).first()
        if not category_id:
            raise HTTPException(status_code=404, detail="Category code not found")

        if category_id.category_code != category_code:
            return ResponseSchema(
                success=False,
                data=None,
                message="category code and id mismatch"
            )

        return ResponseSchema(
            success=True,
            data=[category_id],
            message="Category retrieved successfully" if cat_code and category_id else "No categories found"
        )