import csv
import json
from io import StringIO

from fastapi import HTTPException
from src.utils.redis import  redis_client

from src.category.models import CategoryModel
from src.products.dtos import ProductResponseSchema
from src.products.models import ProductModel


class ProductController:

    # @staticmethod
    # def add_product(body, db):
    #     prod_name = db.query(ProductModel).filter(ProductModel.product_name == body.product_name).first()
    #
    #     if body.product_price == 0:
    #         raise HTTPException(status_code=400, detail="Price cannot be zero")
    #     if body.product_quantity == 0:
    #         raise HTTPException(status_code=400, detail="Quantity cannot be zero")
    #
    #     if prod_name:
    #         raise HTTPException(status_code=400, detail="Product already exists")
    #     ct_id = db.query(CategoryModel).filter(CategoryModel.id == body.category_id).first()
    #     if not ct_id:
    #         raise HTTPException(status_code=400, detail="Category does not exist")
    #
    #     product = ProductModel(
    #     product_name= body.product_name,
    #     product_price= body.product_price,
    #     product_quantity= body.product_quantity,
    #     product_description= body.product_description,
    #     category_id= body.category_id
    #
    #     )
    #     db.add(product)
    #     db.commit()
    #     db.refresh(product)
    #     return ProductResponseSchema(
    #        product_id=product.product_id,
    #         product_name = product.product_name
    #
    #     )

    @staticmethod
    def add_product_by_category_id(category_id, body, db):
        category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category does not exist")

        prod_name = db.query(ProductModel).filter(ProductModel.product_name == body.product_name,
                                                  ProductModel.category_id==category_id).first()

        if body.product_price <=0 or body.product_quantity <=0:
            raise HTTPException(status_code=400, detail="Quantity or price cannot be zero")

        if prod_name:
            raise HTTPException(status_code=400, detail="Product already exists")

        product = ProductModel(
            product_name=body.product_name,
            product_price=body.product_price,
            product_quantity=body.product_quantity,
            product_description=body.product_description,
            category_id = category.id

        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return ProductResponseSchema(
            product_id=product.product_id,
            product_name=product.product_name

        )

    @staticmethod
    def add_bulk_products_by_csv(category_id, file, db):
        category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category does not exist")


        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="File must be a CSV file")

        contents = file.file.read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(contents))
        products_to_add = []
        errors = []

        for idx, row in enumerate(csv_reader, start=1):
            try:
                name = row.get("product_name")
                price = float(row.get("product_price"))
                product_description = row.get("product_description")
                quantity = int(row.get("product_quantity"))

                is_prod_exist = db.query(ProductModel).filter(ProductModel.product_name == name).first()

                if is_prod_exist:
                    raise ValueError("Product name already exists")

                if price <= 0 or quantity <= 0:
                    raise ValueError("Price or quantity cannot be 0")

                product = ProductModel(
                    product_name=name,
                    product_price=price,
                    product_quantity=quantity,
                    product_description=product_description,
                    category_id = category_id
                )

                products_to_add.append(product)

            except Exception as e:
                errors.append({
                    "row": idx,
                    "product_name": row.get("product_name"),
                    "error": str(e)
                })

        if products_to_add:
            db.bulk_save_objects(products_to_add)
            db.commit()

        return {
            "success": True,
            "inserted_count": len(products_to_add),
            "failed_count": len(errors),
            "errors": errors
        }


    @staticmethod
    def get_all_products(limit,db):
        products_list = db.query(ProductModel).limit(limit).all()

        return {
            "Success": True,
             "data" :products_list,
             "count": limit
        }


    @staticmethod
    async def get_product_by_product_id(product_id, db):
        cache_data = f"product:{product_id}"
        get_product_id = await redis_client.get(cache_data)
        if get_product_id:
            return json.loads(get_product_id)

        get_by_product_id = db.query(ProductModel).filter(ProductModel.product_id == product_id).first()

        if not get_by_product_id:
            raise HTTPException(status_code=404, detail="Product does not exist")

        product_data = {
            "id": get_by_product_id.product_id,
            "product_name": get_by_product_id.product_name,
            "product_description": get_by_product_id.product_description,
            "product_price": get_by_product_id.product_price,
            "product_quantity": get_by_product_id.product_quantity,
        }

        await redis_client.set(cache_data, json.dumps(product_data), ex=60)

        return product_data


    @staticmethod
    def update_a_product_by_id(product_id, body, db):
        get_by_id = db.query(ProductModel).filter(ProductModel.product_id == product_id).first()
        if not get_by_id:
            raise HTTPException(status_code=404, detail="Product does not exist")

        update_data = body.model_dump()
        for key, value in update_data.items():
            setattr(get_by_id, key, value)

        db.commit()
        db.refresh(get_by_id)

        return get_by_id

