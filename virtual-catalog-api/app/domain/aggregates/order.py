from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from decimal import Decimal
from app.domain.value_objects.price import Price
from app.domain.value_objects.order_item import OrderItem
from app.domain.exceptions import DomainException


class OrderStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    id: str
    user_id: str
    status: OrderStatus
    created_at: datetime
    _items: List[OrderItem] = field(default_factory=list)

    @classmethod
    def create(cls, order_id: str, user_id: str, items: List[OrderItem]) -> "Order":
        if not items:
            raise DomainException("An order must contain at least one item.")

        return cls(
            id=order_id,
            user_id=user_id,
            status=OrderStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            _items=list(items),
        )

    def pay(self):
        if self.status != OrderStatus.PENDING:
            raise DomainException(
                f"Cannot pay an order that is currently {self.status.value}."
            )

        self.status = OrderStatus.PAID

    def cancel(self):
        if self.status == OrderStatus.CANCELLED:
            raise DomainException("The order is already cancelled.")
        if self.status == OrderStatus.PAID:
            raise DomainException("Cannot cancel an order that has already been paid.")

        self.status = OrderStatus.CANCELLED

    def get_items(self) -> List[OrderItem]:
        return list(self._items)

    @property
    def total_amount(self) -> Price:
        if not self._items:
            return Price(Decimal("0.00"), "COP")

        currency = self._items[0].unit_price.currency
        total_sum = sum((item.subtotal for item in self._items), Decimal("0.00"))

        return Price(total_sum, currency)

    @classmethod
    def reconstitute(
        cls,
        order_id: str,
        user_id: str,
        status_value: str,
        created_at: datetime,
        items: List[OrderItem],
    ) -> "Order":
        order = cls(
            id=order_id,
            user_id=user_id,
            status=OrderStatus(status_value),
            created_at=created_at,
        )
        order._items = items
        return order
