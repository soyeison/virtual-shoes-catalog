from typing import List
from app.domain.aggregates.article import Article
from app.application.ports.article_repository import ArticleRepository


class GetAllArticlesUseCase:
    def __init__(self, article_repository: ArticleRepository):
        self.article_repository = article_repository

    def execute(self) -> List[Article]:
        return self.article_repository.find_all()
