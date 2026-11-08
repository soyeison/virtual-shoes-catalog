from abc import ABC, abstractmethod


class ArticleStockChecker(ABC):
    @abstractmethod
    def has_sufficient_stock(self, article_id: str, requested_quantity: int) -> bool:
        pass
