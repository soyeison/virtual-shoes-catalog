import uuid
from typing import List
from decimal import Decimal
from app.domain.aggregates.article import Article
from app.domain.value_objects.image_url import ImageURL
from app.domain.value_objects.price import Price
from app.domain.value_objects.stock import Stock
from app.application.ports.article_repository import ArticleRepository


class CreateArticleUseCase:
    def __init__(self, article_repository: ArticleRepository):
        self.article_repository = article_repository

    def execute(
        self,
        name: str,
        description: str,
        stock_qty: int,
        price_amount: float,
        price_currency: str,
        image_urls: List[str],
    ):
        price = Price(amount=Decimal(str(price_amount)), currency=price_currency)
        stock = Stock(value=stock_qty)

        article = Article.create(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            initial_stock=stock,
            initial_price=price,
        )

        for url in image_urls:
            article.attach_image(ImageURL(url))

        self.article_repository.create(article)

        return article
