from unittest.mock import MagicMock
from app.application.services.stock_checker_service import StockCheckerService
from app.domain.aggregates.article import Article, Stock, Price
from decimal import Decimal


def test_stock_checker_returns_true_if_stock_is_sufficient():
    # Arrange
    mock_article_repo = MagicMock()
    mock_article = Article.create(
        "art-1", "Name", "Desc", Stock(10), Price(Decimal("100"), "COP")
    )
    mock_article_repo.find_by_id.return_value = mock_article

    service = StockCheckerService(mock_article_repo)

    # Act & Assert
    assert service.has_sufficient_stock("art-1", 5) is True
    assert service.has_sufficient_stock("art-1", 10) is True


def test_stock_checker_returns_false_if_stock_insufficient_or_article_missing():
    # Arrange
    mock_article_repo = MagicMock()
    mock_article = Article.create(
        "art-1", "Name", "Desc", Stock(5), Price(Decimal("100"), "COP")
    )
    mock_article_repo.find_by_id.return_value = mock_article

    service = StockCheckerService(mock_article_repo)

    # Act & Assert
    assert service.has_sufficient_stock("art-1", 6) is False

    # Test missing article
    mock_article_repo.find_by_id.return_value = None
    assert service.has_sufficient_stock("art-invalid", 1) is False
