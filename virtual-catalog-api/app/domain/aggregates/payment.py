from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
from app.domain.value_objects.price import Price
from app.domain.exceptions import DomainException


class PaymentStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Payment:
    id: str
    order_id: str
    amount: Price
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def initialize(cls, payment_id: str, order_id: str, amount: Price) -> "Payment":
        now = datetime.now(timezone.utc)
        return cls(
            id=payment_id,
            order_id=order_id,
            amount=amount,
            status=PaymentStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

    def mark_as_successful(self):
        if self.status != PaymentStatus.PENDING:
            raise DomainException(
                f"Cannot mark as successful. Payment is currently {self.status.value}."
            )

        self.status = PaymentStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def mark_as_failed(self):
        if self.status != PaymentStatus.PENDING:
            raise DomainException(
                f"Cannot mark as failed. Payment is currently {self.status.value}."
            )

        self.status = PaymentStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)

    @classmethod
    def reconstitute(
        cls,
        payment_id: str,
        order_id: str,
        amount: Price,
        status_value: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> "Payment":
        return cls(
            id=payment_id,
            order_id=order_id,
            amount=amount,
            status=PaymentStatus(status_value),
            created_at=created_at,
            updated_at=updated_at,
        )
