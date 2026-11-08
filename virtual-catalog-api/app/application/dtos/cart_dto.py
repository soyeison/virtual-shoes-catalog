from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CartItemDTO:
    article_id: str
    name: str
    quantity: int
    unit_price: float
    subtotal: float
    image_url: Optional[str]


@dataclass
class CartDTO:
    user_id: str
    items: List[CartItemDTO]
    total_amount: float
