"""Small helpers shared by agent tool modules."""

import json
from decimal import Decimal
from typing import Any


def json_result(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def amount_to_paise(amount_rupees: float) -> int:
    amount = Decimal(str(amount_rupees))
    paise = amount * 100
    if amount <= 0 or paise != paise.to_integral_value():
        raise ValueError("Enter a positive amount with no more than two decimal places")
    return int(paise)
