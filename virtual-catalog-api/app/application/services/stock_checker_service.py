from app.domain.aggregates.cart import ArticleStockChecker
from app.application.ports.article_repository import ArticleRepository


class StockCheckerService(ArticleStockChecker):
    def __init__(self, article_repo: ArticleRepository):
        self.article_repo = article_repo

    def has_sufficient_stock(self, article_id: str, requested_quantity: int) -> bool:
        article = self.article_repo.find_by_id(article_id)

        if not article:
            return False

        return article.get_stock().value >= requested_quantity
