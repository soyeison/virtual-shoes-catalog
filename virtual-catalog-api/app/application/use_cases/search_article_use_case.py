import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
from app.domain.aggregates.article import Article
from app.application.ports.article_repository import ArticleRepository
from app.application.queries.article_criteria import ArticleCriteria


@dataclass
class PaginatedArticlesResult:
    items: List[Article]
    total_records: int
    total_pages: int
    current_page: int


class SearchArticleUseCase:
    def __init__(self, article_repository: ArticleRepository):
        self.article_repository = article_repository

    def execute(
        self,
        name: Optional[str],
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedArticlesResult:
        offset = (page - 1) * page_size

        criteria = ArticleCriteria(
            name_contains=name,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            limit=page_size,
            offset=offset,
        )

        articles, total_records = self.article_repository.search(criteria)

        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1

        return PaginatedArticlesResult(
            items=articles,
            total_records=total_records,
            total_pages=total_pages,
            current_page=page,
        )
