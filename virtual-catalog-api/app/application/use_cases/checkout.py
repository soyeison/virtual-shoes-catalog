import uuid
from typing import List
from app.domain.aggregates.cart import Cart
from app.domain.aggregates.order import Order, OrderItem
from app.domain.exceptions import DomainException
from app.application.ports.cart_repository import CartRepository
from app.application.ports.article_repository import ArticleRepository
from app.application.ports.order_repository import OrderRepository


class CheckoutUseCase:
    def __init__(
        self,
        cart_repository: CartRepository,
        article_repository: ArticleRepository,
        order_repository: OrderRepository,
    ):
        self.cart_repository = cart_repository
        self.article_repository = article_repository
        self.order_repository = order_repository

    def execute(self, user_id: str) -> Order:
        cart = self.cart_repository.find_by_user_id(user_id)
        if not cart or cart.is_empty:
            raise DomainException("Cannot proceed to checkout with an empty cart.")

        order_items: List[OrderItem] = []

        for cart_item in cart.get_items():
            article = self.article_repository.find_by_id(cart_item.article_id)

            if not article:
                raise DomainException(
                    f"Article {cart_item.article_id} is no longer available in the catalog."
                )

            article.decrease_stock(cart_item.quantity)

            self.article_repository.update(article)

            frozen_item = OrderItem(
                article_id=article.id,
                quantity=cart_item.quantity,
                unit_price=article.get_price(),
            )
            order_items.append(frozen_item)

        order_id = f"ord-{uuid.uuid4().hex[:8]}"

        new_order = Order.create(order_id=order_id, user_id=user_id, items=order_items)

        self.order_repository.save(new_order)

        cart.clear()
        self.cart_repository.save(cart)

        return new_order
