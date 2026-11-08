import pytest
from unittest.mock import MagicMock
from app.application.use_cases.create_article import CreateArticleUseCase
from app.application.use_cases.search_article_use_case import SearchArticleUseCase
from app.application.queries.article_criteria import ArticleCriteria
from app.domain.aggregates.article import Article, Stock, Price


@pytest.fixture
def mock_article_repository():
    return MagicMock()


def test_create_article_use_case_executes_complete_flow(mock_article_repository):
    # Arrange
    use_case = CreateArticleUseCase(article_repository=mock_article_repository)

    # Act
    new_article = use_case.execute(
        name="Zapatos Deportivos",
        description="Zapatos deportivos para correr con suela antideslizante",
        stock_qty=15,
        price_amount=120000.0,
        price_currency="COP",
        image_urls=["http://localhost/mouse1.jpg", "http://localhost/mouse2.jpg"],
    )

    assert new_article.name == "Zapatos Deportivos"
    assert isinstance(new_article.get_stock(), Stock)
    assert new_article.get_stock().value == 15
    assert new_article.get_price().amount == 120000.0
    assert len(new_article.get_image_urls()) == 2

    # 2. Verify the repository was invoked to persist the created article
    mock_article_repository.create.assert_called_once_with(new_article)


def test_search_articles_use_case_builds_criteria_correctly(mock_article_repository):
    # Arrange
    use_case = SearchArticleUseCase(article_repository=mock_article_repository)
    mock_article_repository.search.return_value = ([], 0)  # Simulated empty list return

    # Act
    use_case.execute(
        name="Zapatos Adidas",
        min_price=50000.0,
        max_price=200000.0,
        sort_by="price_asc",
        page=2,
        page_size=10,
    )

    # Assert
    # Capture the argument with which the repository's 'search' method was called
    mock_article_repository.search.assert_called_once()
    args, _ = mock_article_repository.search.call_args
    submitted_criteria = args[0]

    # Validate the mapping to the 'Criteria' query object is perfect
    assert isinstance(submitted_criteria, ArticleCriteria)
    assert submitted_criteria.name_contains == "Zapatos Adidas"
    assert submitted_criteria.min_price == 50000.0
    assert submitted_criteria.max_price == 200000.0
    assert submitted_criteria.sort_by == "price_asc"
    assert submitted_criteria.limit == 10
    assert submitted_criteria.offset == 10
