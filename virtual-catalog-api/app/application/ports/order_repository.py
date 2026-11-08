from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.aggregates.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> List[Order]:
        pass
