"""FastAPI application for the Dukaan Dost dashboard.
Run from the project folder with: uvicorn backend.main:app --reload
"""
import os
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg
from redis.asyncio import Redis

from .db_utils import agent_log_utils, catalog_utils, credit_utils, customer_utils, restock_utils
from .schemas import CreditInput, CreditUpdate, ItemInput, NameInput
from .agent import router as agent_router
from .auth.auth import router as auth_router
from .auth.dependencies import get_current_user
from .database import init_db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    app.state.redis = Redis.from_url(redis_url, decode_responses=True)
    try:
        await app.state.redis.ping()
        yield
    finally:
        await app.state.redis.aclose()


app = FastAPI(title="Dukaan Dost API", version="0.1.0", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(agent_router, prefix="/agent", tags=["agent"])
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def check_browser_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and origin and origin not in FRONTEND_ORIGINS:
        return JSONResponse(status_code=403, content={"detail": "Untrusted request origin"})
    return await call_next(request)


@app.exception_handler(psycopg.IntegrityError)
async def integrity_error_handler(request: Request, exc: psycopg.IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "This conflicts with existing data or references an unknown category/customer"},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/agent-logs")
def list_agent_logs(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
):
    return agent_log_utils.get_agent_logs(user["id"], limit=limit, offset=offset)


@app.get("/categories")
def list_categories(user: dict = Depends(get_current_user)):
    return catalog_utils.get_all_categories(user["shop_id"])


@app.post("/categories", status_code=201)
def create_category(data: NameInput, user: dict = Depends(get_current_user)):
    return {"id": catalog_utils.add_category(data.name, user["shop_id"]), "name": data.name.strip()}


@app.delete("/categories/{category_id}")
def delete_category(category_id: int, user: dict = Depends(get_current_user)):
    if not catalog_utils.delete_category(category_id, user["shop_id"]):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"deleted": True}


@app.get("/items")
def list_items(category_id: int | None = Query(default=None, gt=0), user: dict = Depends(get_current_user)):
    if category_id is None:
        return catalog_utils.get_all_items(user["shop_id"])
    return catalog_utils.get_items_by_category(category_id, user["shop_id"])


@app.post("/items", status_code=201)
def create_item(data: ItemInput, user: dict = Depends(get_current_user)):
    item_id = catalog_utils.add_item(data.name, data.category_id, user["shop_id"])
    return {"id": item_id, "name": data.name.strip(), "category_id": data.category_id}


@app.delete("/items/{item_id}")
def delete_item(item_id: int, user: dict = Depends(get_current_user)):
    if not catalog_utils.delete_item(item_id, user["shop_id"]):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": True}


@app.get("/restock-items")
def list_restock_items(category_id: int | None = Query(default=None, gt=0), user: dict = Depends(get_current_user)):
    if category_id is None:
        return restock_utils.get_all_restock_items(user["shop_id"])
    return restock_utils.get_restock_items_by_category(category_id, user["shop_id"])


@app.post("/restock-items", status_code=201)
def create_restock_item(data: ItemInput, user: dict = Depends(get_current_user)):
    item_id = restock_utils.add_restock_item(data.name, data.category_id, user["shop_id"])
    return {"id": item_id, "name": data.name.strip(), "category_id": data.category_id}


@app.delete("/restock-items")
def clear_restock_list(user: dict = Depends(get_current_user)):
    return {"deleted_count": restock_utils.delete_all_restock_items(user["shop_id"])}


@app.delete("/restock-items/{item_id}")
def delete_restock_item(item_id: int, user: dict = Depends(get_current_user)):
    if not restock_utils.remove_restock_item(item_id, user["shop_id"]):
        raise HTTPException(status_code=404, detail="Restock item not found")
    return {"deleted": True}


@app.get("/customers")
def list_customers(user: dict = Depends(get_current_user)):
    return customer_utils.get_all_customers(user["shop_id"])


@app.post("/customers", status_code=201)
def create_customer(data: NameInput, user: dict = Depends(get_current_user)):
    return {
        "id": customer_utils.add_customer(data.name, user["shop_id"]),
        "name": data.name.strip(),
        "total_paise": 0,
    }


@app.get("/credit-records")
def list_credit_records(
    entry_date: date | None = None,
    customer_id: int | None = Query(default=None, gt=0),
    user: dict = Depends(get_current_user),
):
    shop_id = user["shop_id"]
    if customer_id is not None:
        records = credit_utils.get_credit_records_by_customer_id(customer_id, shop_id)
        if entry_date is not None:
            records = [r for r in records if r["entry_date"] == entry_date.isoformat()]
        return records
    if entry_date is not None:
        return credit_utils.get_credit_records_by_date(entry_date.isoformat(), shop_id)
    return credit_utils.get_all_credit_records(shop_id)


@app.post("/credit-records", status_code=201)
def create_credit_record(data: CreditInput, user: dict = Depends(get_current_user)):
    record_id = credit_utils.add_credit_record(
        data.customer,
        data.amount_paise,
        user["shop_id"],
        data.description,
        data.entry_date.isoformat() if data.entry_date else None,
    )
    return {"id": record_id}


@app.patch("/credit-records/{record_id}")
def update_credit_record(record_id: int, data: CreditUpdate, user: dict = Depends(get_current_user)):
    updated = credit_utils.update_credit_record(
        record_id,
        user["shop_id"],
        customer=data.customer,
        amount_paise=data.amount_paise,
        description=data.description,
        entry_date=data.entry_date.isoformat() if data.entry_date else None,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Credit record not found or no fields supplied")
    return {"updated": True}


@app.delete("/credit-records/{record_id}")
def delete_credit_record(record_id: int, user: dict = Depends(get_current_user)):
    if not credit_utils.delete_credit_record(record_id, user["shop_id"]):
        raise HTTPException(status_code=404, detail="Credit record not found")
    return {"deleted": True}


@app.delete("/customers/{customer_id}/credit-records")
def clear_customer_credit_records(customer_id: int, user: dict = Depends(get_current_user)):
    shop_id = user["shop_id"]
    customer = next(
        (c for c in customer_utils.get_all_customers(shop_id) if c["id"] == customer_id), None
    )
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    deleted_count = credit_utils.delete_customer_credit_records(customer["name"], shop_id)
    return {"deleted_count": deleted_count}
