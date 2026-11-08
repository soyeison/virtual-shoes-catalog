from dataclasses import dataclass
from app.domain.exceptions import DomainException


@dataclass(frozen=True)
class Stock:
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise DomainException("Stock value cannot be negative")

    def decrease(self, quantity: int):
        if quantity < 0:
            raise DomainException("Quantity to decrease cannot be negative")
        if quantity > self.value:
            raise DomainException("Cannot decrease stock below zero")

        return Stock(self.value - quantity)

    def add(self, quantity: int):
        if quantity <= 0:
            raise DomainException("Quantity to add must be positive")

        return Stock(self.value + quantity)
