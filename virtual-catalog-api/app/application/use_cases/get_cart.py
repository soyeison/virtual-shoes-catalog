from app.application.ports.cart_repository import CartRepository
from app.application.ports.article_repository import ArticleRepository
from app.domain.aggregates.cart import Cart
from app.application.dtos.cart_dto import CartDTO, CartItemDTO


class GetCartUseCase:
    def __init__(self, cart_repo: CartRepository, article_repo: ArticleRepository):
        self.cart_repo = cart_repo
        self.article_repo = article_repo

    def execute(self, user_id: str) -> CartDTO:
        cart = self.cart_repo.find_by_user_id(user_id)
        if not cart:
            cart = Cart.initialize(user_id)
            self.cart_repo.save(cart)

        item_dtos = []
        total_amount = 0.0

        for item in cart.get_items():
            article = self.article_repo.find_by_id(item.article_id)

            # Defensive programming: In case an article was hard-deleted from the database
            if article:
                unit_price = float(article.get_price().amount)
                subtotal = unit_price * item.quantity
                total_amount += subtotal

                # Safely get the first image as thumbnail, or None if it has no images
                images = article.get_image_urls()
                main_image = images[0].url if images else None

                item_dtos.append(
                    CartItemDTO(
                        article_id=article.id,
                        name=article.name,
                        quantity=item.quantity,
                        unit_price=unit_price,
                        subtotal=subtotal,
                        image_url=main_image,
                    )
                )

        return CartDTO(user_id=cart.user_id, items=item_dtos, total_amount=total_amount)
