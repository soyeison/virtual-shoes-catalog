from app.domain.aggregates.cart import Cart
from app.application.ports.cart_repository import CartRepository
from app.application.ports.article_repository import ArticleRepository
from app.application.services.stock_checker_service import StockCheckerService


class AddItemToCartUseCase:
    def __init__(self, cart_repo: CartRepository, article_repo: ArticleRepository):
        self.cart_repo = cart_repo
        self.article_repo = article_repo

    def execute(self, user_id: str, article_id: str, quantity: int) -> Cart:
        cart = self.cart_repo.find_by_user_id(user_id)
        if not cart:
            cart = Cart.initialize(user_id)

        stock_checker = StockCheckerService(self.article_repo)

        # The Cart will throw a DomainException if business limits or stock checks fail
        cart.add_item(article_id, quantity, stock_checker)

        self.cart_repo.save(cart)

        return cart
