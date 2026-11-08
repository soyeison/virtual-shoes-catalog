from dataclasses import dataclass
from decimal import Decimal
from app.domain.exceptions import DomainException


@dataclass(frozen=True)
class Price:
    amount: Decimal
    currency: str = "COP"

    def __post_init__(self):
        if self.amount < 0:
            raise DomainException("Price amount cannot be negative")
        if not self.currency:
            raise DomainException("Currency cannot be empty")
        if len(self.currency) != 3:
            raise DomainException("Currency must be a 3-letter code")

    def add(self, other: "Price") -> "Price":
        if self.currency != other.currency:
            raise DomainException("Cannot add prices with different currencies")

        return Price(amount=self.amount + other.amount, currency=self.currency)
