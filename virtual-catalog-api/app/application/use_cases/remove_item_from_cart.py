from app.domain.aggregates.cart import Cart
from app.application.ports.cart_repository import CartRepository


class RemoveItemFromCartUseCase:
    def __init__(self, cart_repository: CartRepository):
        self.cart_repository = cart_repository

    def execute(self, user_id: str, article_id: str) -> Cart:
        cart = self.cart_repository.find_by_user_id(user_id)

        if not cart:
            return Cart.initialize(user_id)

        cart.remove_item(article_id)

        self.cart_repository.save(cart)

        return cart
