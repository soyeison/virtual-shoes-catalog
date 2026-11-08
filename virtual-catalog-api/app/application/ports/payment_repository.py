from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.aggregates.payment import Payment


class PaymentRepository(ABC):
    @abstractmethod
    def save(self, payment: Payment) -> None:
        pass

    @abstractmethod
    def find_by_id(self, payment_id: str) -> Optional[Payment]:
        pass

    @abstractmethod
    def find_by_order_id(self, order_id: str) -> List[Payment]:
        pass
