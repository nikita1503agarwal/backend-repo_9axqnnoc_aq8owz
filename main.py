import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import MlbbPackage, Order

app = FastAPI(title="Game Top-up API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Game Top-up Backend Running"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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
            response["database_url"] = "✅ Configured"
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

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# ---------- Seed route for initial MLBB packages (idempotent) ----------
@app.post("/seed/mlbb", response_model=List[MlbbPackage])
def seed_mlbb_packages():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    default_packages = [
        {"name": "86 Diamonds", "diamonds": 86, "bonus": 0, "price": 1.99, "popular": False},
        {"name": "172 Diamonds", "diamonds": 172, "bonus": 12, "price": 3.69, "popular": True},
        {"name": "257 Diamonds", "diamonds": 257, "bonus": 25, "price": 5.49, "popular": False},
        {"name": "344 Diamonds", "diamonds": 344, "bonus": 32, "price": 7.29, "popular": False},
        {"name": "570 Diamonds", "diamonds": 570, "bonus": 60, "price": 11.49, "popular": True},
        {"name": "1156 Diamonds", "diamonds": 1156, "bonus": 140, "price": 22.99, "popular": False},
    ]

    # Ensure unique by diamonds count
    existing = {p.get("diamonds") for p in db["mlbbpackage"].find({}, {"diamonds": 1})}
    to_insert = [p for p in default_packages if p["diamonds"] not in existing]

    if to_insert:
        db["mlbbpackage"].insert_many(to_insert)

    docs = list(db["mlbbpackage"].find().sort("diamonds", 1))
    return [MlbbPackage(**{
        "name": d.get("name"),
        "diamonds": d.get("diamonds"),
        "bonus": d.get("bonus", 0),
        "price": float(d.get("price")),
        "popular": d.get("popular", False)
    }) for d in docs]

# ---------- Public endpoints ----------
@app.get("/api/mlbb/packages")
def list_packages():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    docs = list(db["mlbbpackage"].find().sort("diamonds", 1))
    # Return with _id string
    for d in docs:
        d["_id"] = str(d["_id"]) 
        d["price"] = float(d.get("price", 0))
    return {"packages": docs}

class CreateOrderRequest(BaseModel):
    player_id: str
    server_id: str
    package_id: str
    contact_email: Optional[str] = None

@app.post("/api/mlbb/order")
def create_order(payload: CreateOrderRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    # Validate package
    try:
        pkg = db["mlbbpackage"].find_one({"_id": ObjectId(payload.package_id)})
    except Exception:
        pkg = None
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")

    order_doc = {
        "game": "mlbb",
        "player_id": payload.player_id.strip(),
        "server_id": payload.server_id.strip(),
        "package_id": str(pkg["_id"]),
        "package_name": pkg.get("name"),
        "diamonds": pkg.get("diamonds"),
        "price": float(pkg.get("price", 0)),
        "contact_email": payload.contact_email,
        "status": "pending",
    }

    order_id = create_document("order", order_doc)
    return {"order_id": order_id, "status": "pending"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
