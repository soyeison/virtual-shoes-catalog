import pytest
from unittest.mock import MagicMock, patch
from app.application.use_cases.get_cart import GetCartUseCase
from app.application.use_cases.add_item_to_cart import AddItemToCartUseCase
from app.domain.aggregates.cart import Cart
from app.domain.aggregates.article import Article, Stock, Price
from decimal import Decimal


@pytest.fixture
def mock_cart_repo():
    return MagicMock()


@pytest.fixture
def mock_article_repo():
    return MagicMock()


def test_get_cart_use_case_initializes_and_enriches_dto(
    mock_cart_repo, mock_article_repo
):
    # Arrange
    use_case = GetCartUseCase(mock_cart_repo, mock_article_repo)

    # Simulate cart exists with 1 item
    existing_cart = Cart.initialize("user-1")
    existing_cart._items = {"art-1": MagicMock(article_id="art-1", quantity=2)}
    mock_cart_repo.find_by_user_id.return_value = existing_cart

    # Simulate article exists in catalog
    mock_article = Article.create(
        "art-1", "Mouse", "Desc", Stock(10), Price(Decimal("50.0"), "COP")
    )
    mock_article_repo.find_by_id.return_value = mock_article

    # Act
    cart_dto = use_case.execute("user-1")

    # Assert
    assert cart_dto.user_id == "user-1"
    assert len(cart_dto.items) == 1
    assert cart_dto.items[0].name == "Mouse"
    assert cart_dto.items[0].subtotal == 100.0  # 50.0 * 2
    assert cart_dto.total_amount == 100.0


@patch("app.application.use_cases.add_item_to_cart.StockCheckerService")
def test_add_item_to_cart_use_case_orchestrates_correctly(
    MockStockChecker, mock_cart_repo, mock_article_repo
):
    # Arrange
    use_case = AddItemToCartUseCase(mock_cart_repo, mock_article_repo)

    # Simulate new cart initialized
    mock_cart_repo.find_by_user_id.return_value = None

    # Setup the mocked service to allow adding items
    mock_service_instance = MockStockChecker.return_value
    mock_service_instance.has_sufficient_stock.return_value = True

    # Act
    updated_cart = use_case.execute("user-new", "art-1", 3)

    # Assert
    assert updated_cart.user_id == "user-new"
    assert len(updated_cart.get_items()) == 1
    mock_cart_repo.save.assert_called_once_with(updated_cart)
