from dataclasses import dataclass
from app.domain.exceptions import DomainException


@dataclass(frozen=True)
class CartItem:
    article_id: str
    quantity: int

    def __post_init__(self):
        if self.quantity < 1:
            raise DomainException("Quantity must be at least 1")

    def change_quantity(self, new_quantity: int) -> "CartItem":
        return CartItem(article_id=self.article_id, quantity=new_quantity)
