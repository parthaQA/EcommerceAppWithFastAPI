from fastapi import FastAPI

from src.products.router import product_routes
from src.utils.db import BASE, engine
from src.customers.router import customer_routes
from src.category.router import category_routes
from src.cart.router import cart_routes
from src.utils.redis import redis_client

BASE.metadata.create_all(engine)

app = FastAPI(title="This is my ecommerce application")
app.include_router(customer_routes)
app.include_router(category_routes)
app.include_router(product_routes)
app.include_router(cart_routes)

@app.on_event("startup")
async def startup():

    response = await redis_client.ping()

    print("Redis Connected:", response)


@app.on_event("shutdown")
async def shutdown():

    await redis_client.close()


@app.get("/redis-test")
async def redis_test():

    await redis_client.set("name", "Partha")

    value = await redis_client.get("name")

    return {
        "value": value
    }