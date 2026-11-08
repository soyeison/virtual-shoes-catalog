from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from app.domain.aggregates.article import Article
from app.application.queries.article_criteria import ArticleCriteria


class ArticleRepository(ABC):
    @abstractmethod
    def create(self, article: Article) -> None:
        pass

    @abstractmethod
    def update(self, article: Article) -> None:
        pass

    @abstractmethod
    def find_by_id(self, article_id: str) -> Optional[Article]:
        pass

    @abstractmethod
    def find_all(self) -> List[Article]:
        pass

    @abstractmethod
    def search(self, criteria: ArticleCriteria) -> Tuple[List[Article], int]:
        pass
