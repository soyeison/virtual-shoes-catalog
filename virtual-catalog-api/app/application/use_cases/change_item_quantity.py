from app.domain.aggregates.cart import Cart
from app.domain.exceptions import DomainException
from app.application.ports.cart_repository import CartRepository
from app.application.ports.article_repository import ArticleRepository
from app.application.services.stock_checker_service import StockCheckerService


class ChangeItemQuantityUseCase:
    def __init__(
        self, cart_repository: CartRepository, article_repository: ArticleRepository
    ):
        self.cart_repository = cart_repository
        self.article_repository = article_repository

    def execute(self, user_id: str, article_id: str, new_quantity: int) -> Cart:
        cart = self.cart_repository.find_by_user_id(user_id)
        if not cart:
            raise DomainException("Cart not found or empty.")

        stock_checker = StockCheckerService(self.article_repository)
        cart.change_item_quantity(article_id, new_quantity, stock_checker)

        self.cart_repository.save(cart)

        return cart
