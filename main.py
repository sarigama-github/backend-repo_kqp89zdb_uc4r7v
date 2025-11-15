import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "E-Commerce backend ready"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# API models for request bodies
class ProductCreate(Product):
    pass

class OrderCreate(Order):
    pass

@app.get("/api/products")
def list_products(category: Optional[str] = None, limit: int = 20):
    filter_dict = {"category": category} if category else {}
    try:
        products = get_documents("product", filter_dict=filter_dict, limit=limit)
        # Convert ObjectId to str
        for p in products:
            if "_id" in p:
                p["id"] = str(p.pop("_id"))
        return {"items": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products", status_code=201)
def create_product(product: ProductCreate):
    try:
        inserted_id = create_document("product", product)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders", status_code=201)
def create_order(order: OrderCreate):
    try:
        inserted_id = create_document("order", order)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schema")
def get_schema():
    # Expose schemas info for tooling/frontend if needed
    return {
        "collections": ["user", "product", "order"],
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
