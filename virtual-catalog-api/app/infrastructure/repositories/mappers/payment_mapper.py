import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from app.domain.aggregates.payment import Payment, PaymentStatus
from app.domain.aggregates.article import Price


class PaymentMapper:
    @staticmethod
    def to_domain(row: sqlite3.Row | Dict[str, Any]) -> Payment:
        return Payment.reconstitute(
            payment_id=row["id"],
            order_id=row["order_id"],
            amount=Price(amount=Decimal(row["amount"]), currency=row["currency"]),
            status_value=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def to_persistence(payment: Payment) -> tuple:
        return (
            payment.id,
            payment.order_id,
            str(payment.amount.amount),  # Decimal to String
            payment.amount.currency,
            payment.status.value,  # Enum to String
            payment.created_at.isoformat(),
            payment.updated_at.isoformat(),
        )
