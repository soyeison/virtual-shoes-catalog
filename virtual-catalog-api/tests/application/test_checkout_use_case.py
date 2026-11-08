from unittest.mock import MagicMock
from decimal import Decimal
import pytest
from app.domain.aggregates.cart import Cart, CartItem
from app.domain.aggregates.article import Article, Price, Stock
from app.domain.exceptions import DomainException
from app.application.services.stock_checker_service import StockCheckerService
from app.application.use_cases.checkout import CheckoutUseCase


@pytest.fixture
def mocks():
    return {
        "cart_repository": MagicMock(),
        "article_repository": MagicMock(),
        "order_repository": MagicMock(),
    }


def test_checkout_successful_flow(mocks):
    # Arrange: Preparamos los dobles de prueba
    user_id = "usr-123"

    article = Article(
        id="novarun-shoe-1",
        name="NovaRun Speed",
        description="Running shoes",
        image_urls=[],
        price=Price(Decimal("150.00"), "COP"),
        stock=Stock(10),
    )
    mocks["article_repository"].find_by_id.return_value = article

    stockeChecker = StockCheckerService(article_repo=mocks["article_repository"])
    cart = Cart(user_id=user_id)
    cart.add_item(article_id="novarun-shoe-1", quantity=2, stock_checker=stockeChecker)
    mocks["cart_repository"].find_by_user_id.return_value = cart

    use_case = CheckoutUseCase(
        cart_repository=mocks["cart_repository"],
        article_repository=mocks["article_repository"],
        order_repository=mocks["order_repository"],
    )

    # Act
    order = use_case.execute(user_id)

    # Assert
    assert order is not None
    assert order.user_id == user_id
    assert order.total_amount.amount == Decimal("300.00")  # 2 items * 150.00

    assert article.get_stock().value == 8

    mocks["article_repository"].update.assert_called_once_with(article)
    mocks["order_repository"].save.assert_called_once_with(order)
    mocks["cart_repository"].save.assert_called_once_with(cart)

    assert cart.is_empty is True


def test_checkout_fails_with_empty_cart(mocks):
    use_case = CheckoutUseCase(**mocks)
    mocks["cart_repository"].find_by_user_id.return_value = Cart(user_id="usr-1")

    with pytest.raises(DomainException) as exc_info:
        use_case.execute("usr-1")

    assert "empty cart" in str(exc_info.value)
    mocks["order_repository"].save.assert_not_called()
