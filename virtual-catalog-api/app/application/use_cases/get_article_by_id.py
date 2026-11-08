from typing import Optional
from app.domain.aggregates.article import Article
from app.application.ports.article_repository import ArticleRepository


class GetArticleByIdUseCase:
    def __init__(self, article_repository: ArticleRepository):
        self.article_repository = article_repository

    def execute(self, article_id: str) -> Optional[Article]:
        return self.article_repository.find_by_id(article_id)
