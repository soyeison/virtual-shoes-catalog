from typing import Dict, List
from dataclasses import dataclass, field
from app.domain.exceptions import DomainException
from app.domain.value_objects.cart_item import CartItem
from app.domain.services.article_stock_service import ArticleStockChecker


@dataclass
class Cart:
    user_id: str
    _items: Dict[str, CartItem] = field(default_factory=dict)

    MAX_UNITS_PER_ARTICLE = 10

    @classmethod
    def initialize(cls, user_id: str) -> "Cart":
        return cls(user_id=user_id)

    @classmethod
    def reconstitute(cls, user_id: str, items: Dict[str, CartItem]) -> "Cart":
        cart = cls(user_id=user_id)
        cart._items = items
        return cart

    def add_item(
        self, article_id: str, quantity: int, stock_checker: ArticleStockChecker
    ):
        if quantity <= 0:
            raise DomainException("Quantity to add must be greater than zero")

        current_quantity = (
            self._items[article_id].quantity if article_id in self._items else 0
        )
        new_quantity = current_quantity + quantity
        if new_quantity > self.MAX_UNITS_PER_ARTICLE:
            raise DomainException(
                f"Cannot add more than {self.MAX_UNITS_PER_ARTICLE} units of the same article. "
                f"You currently have {current_quantity} in your cart."
            )

        if not stock_checker.has_sufficient_stock(article_id, new_quantity):
            raise DomainException(
                f"Insufficient stock available for article: {article_id}"
            )

        self._items[article_id] = CartItem(article_id=article_id, quantity=new_quantity)

    def change_item_quantity(
        self, article_id: str, new_quantity: int, stock_checker: ArticleStockChecker
    ):
        if article_id not in self._items:
            raise DomainException(f"Article {article_id} is not in the cart.")

        if new_quantity <= 0:
            raise DomainException(
                "Quantity must be greater than zero. Use remove_item instead."
            )

        if new_quantity > self.MAX_UNITS_PER_ARTICLE:
            raise DomainException(
                f"Cannot exceed {self.MAX_UNITS_PER_ARTICLE} units of the same article."
            )

        if not stock_checker.has_sufficient_stock(article_id, new_quantity):
            raise DomainException(
                f"Insufficient stock available for article: {article_id}"
            )

        current_item = self._items[article_id]
        self._items[article_id] = current_item.change_quantity(new_quantity)

    def remove_item(self, article_id: str):
        if article_id in self._items:
            del self._items[article_id]

    def clear(self):
        self._items.clear()

    def get_items(self) -> List[CartItem]:
        return list(self._items.values())

    @property
    def is_empty(self) -> bool:
        return len(self._items) == 0
