"""Pydantic request schemas for the Dukaan Dost API."""
from datetime import date

from pydantic import BaseModel, Field


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
