from abc import ABC, abstractmethod
from typing import Optional
from app.domain.aggregates.cart import Cart


class CartRepository(ABC):
    @abstractmethod
    def save(self, user: Cart) -> None:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Optional[Cart]:
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: str) -> Optional[Cart]:
        pass
