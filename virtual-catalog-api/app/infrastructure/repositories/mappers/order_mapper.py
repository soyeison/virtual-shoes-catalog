import json
import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List
from app.domain.aggregates.order import Order, OrderItem, OrderStatus
from app.domain.aggregates.article import Price


class OrderMapper:
    @staticmethod
    def to_domain(row: sqlite3.Row | Dict[str, Any]) -> Order:
        items_data = json.loads(row["items"]) if row["items"] else []

        order_items = [
            OrderItem(
                article_id=item["article_id"],
                quantity=item["quantity"],
                unit_price=Price(
                    amount=Decimal(item["price_amount"]),
                    currency=item["price_currency"],
                ),
            )
            for item in items_data
        ]

        created_at = datetime.fromisoformat(row["created_at"])

        return Order.reconstitute(
            order_id=row["id"],
            user_id=row["user_id"],
            status_value=row["status"],
            created_at=created_at,
            items=order_items,
        )

    @staticmethod
    def to_persistence(order: Order) -> tuple:
        items_list = [
            {
                "article_id": item.article_id,
                "quantity": item.quantity,
                "price_amount": str(item.unit_price.amount),
                "price_currency": item.unit_price.currency,
            }
            for item in order.get_items()
        ]

        return (
            order.id,
            order.user_id,
            order.status.value,  # Enum to String (e.g., "PENDING")
            order.created_at.isoformat(),  # Datetime to ISO String
            json.dumps(items_list),
        )
