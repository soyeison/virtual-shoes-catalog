from dataclasses import dataclass
from decimal import Decimal
from app.domain.value_objects.price import Price
from app.domain.exceptions import DomainException


@dataclass(frozen=True)
class OrderItem:
    article_id: str
    quantity: int
    unit_price: Price

    def __post_init__(self):
        if self.quantity <= 0:
            raise DomainException("Order item quantity must be greater than zero.")

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price.amount * self.quantity
