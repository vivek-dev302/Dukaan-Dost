"""Simple HTTP API for the Dukaan Dost dashboard.
Run from the project folder with: uvicorn backend.main:app --reload
"""
import sqlite3
from datetime import date

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import utils

app = FastAPI(title="Dukaan Dost API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NameInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ItemInput(NameInput):
    category_id: int = Field(gt=0)


class CreditInput(BaseModel):
    customer: str = Field(min_length=1, max_length=120)
    amount_paise: int = Field(gt=0, description="Integer paise; ₹1 is 100 paise")
    description: str = Field(default="", max_length=500)
    entry_date: date | None = None


class CreditUpdate(BaseModel):
    customer: str | None = Field(default=None, min_length=1, max_length=120)
    amount_paise: int | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=500)
    entry_date: date | None = None


@app.exception_handler(sqlite3.IntegrityError)
async def integrity_error_handler(request: Request, exc: sqlite3.IntegrityError):
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


@app.get("/categories")
def list_categories():
    return utils.get_all_categories()


@app.post("/categories", status_code=201)
def create_category(data: NameInput):
    return {"id": utils.add_category(data.name), "name": data.name.strip()}


@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    if not utils.delete_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"deleted": True}


@app.get("/items")
def list_items(category_id: int | None = Query(default=None, gt=0)):
    return utils.get_all_items() if category_id is None else utils.get_items_by_category(category_id)


@app.post("/items", status_code=201)
def create_item(data: ItemInput):
    item_id = utils.add_item(data.name, data.category_id)
    return {"id": item_id, "name": data.name.strip(), "category_id": data.category_id}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if not utils.delete_item(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": True}


@app.get("/restock-items")
def list_restock_items(category_id: int | None = Query(default=None, gt=0)):
    return (utils.get_all_restock_items() if category_id is None
            else utils.get_restock_items_by_category(category_id))


@app.post("/restock-items", status_code=201)
def create_restock_item(data: ItemInput):
    item_id = utils.add_restock_item(data.name, data.category_id)
    return {"id": item_id, "name": data.name.strip(), "category_id": data.category_id}


@app.delete("/restock-items")
def clear_restock_list():
    return {"deleted_count": utils.delete_all_restock_items()}


@app.delete("/restock-items/{item_id}")
def delete_restock_item(item_id: int):
    if not utils.remove_restock_item(item_id):
        raise HTTPException(status_code=404, detail="Restock item not found")
    return {"deleted": True}


@app.get("/customers")
def list_customers():
    return utils.get_all_customers()


@app.post("/customers", status_code=201)
def create_customer(data: NameInput):
    return {"id": utils.add_customer(data.name), "name": data.name.strip(), "total_paise": 0}


@app.get("/credit-records")
def list_credit_records(
    entry_date: date | None = None,
    customer_id: int | None = Query(default=None, gt=0),
):
    if customer_id is not None:
        records = utils.get_credit_records_by_customer_id(customer_id)
        if entry_date is not None:
            records = [r for r in records if r["entry_date"] == entry_date.isoformat()]
        return records
    if entry_date is not None:
        return utils.get_credit_records_by_date(entry_date.isoformat())
    return utils.get_all_credit_records()


@app.post("/credit-records", status_code=201)
def create_credit_record(data: CreditInput):
    record_id = utils.add_credit_record(
        data.customer,
        data.amount_paise,
        data.description,
        data.entry_date.isoformat() if data.entry_date else None,
    )
    return {"id": record_id}


@app.patch("/credit-records/{record_id}")
def update_credit_record(record_id: int, data: CreditUpdate):
    updated = utils.update_credit_record(
        record_id,
        customer=data.customer,
        amount_paise=data.amount_paise,
        description=data.description,
        entry_date=data.entry_date.isoformat() if data.entry_date else None,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Credit record not found or no fields supplied")
    return {"updated": True}


@app.delete("/credit-records/{record_id}")
def delete_credit_record(record_id: int):
    if not utils.delete_credit_record(record_id):
        raise HTTPException(status_code=404, detail="Credit record not found")
    return {"deleted": True}


@app.delete("/customers/{customer_id}/credit-records")
def clear_customer_credit_records(customer_id: int):
    customer = next(
        (c for c in utils.get_all_customers() if c["id"] == customer_id), None
    )
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    deleted_count = utils.delete_customer_credit_records(customer["name"])
    return {"deleted_count": deleted_count}
