from fastapi import FastAPI, Request


app = FastAPI()

products = {
    "products": [
        {"id": 1, "name": "Product 1", "price": "10"},
        {"id": 2, "name": "Product 2", "price": "20"},
        {"id": 3, "name": "Product 3", "price": "30"}
    ]
}

@app.get("/products")
def get_all_products():
    return products

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products["products"]:
        if product["id"] == product_id:
            return product

    return {"error": "Product not found"}


@app.get("/product/price")
def get_products_by_price(request: Request):
    print(dict(request.query_params))
    price = request.query_params.get("price")
    for product in products["products"]:
        if product["price"] == price:
            return product

    return {"error": "Product price not found", "price": price}


@app.post("/add-product")
def add_product():
    new_product = {
        "id": 4,
        "name": "watch",
        "price": "100"
    }
    print(new_product)
    products["products"].append(new_product)
    return new_product