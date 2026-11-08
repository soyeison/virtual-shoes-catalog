import pytest
from unittest.mock import MagicMock
from app.domain.aggregates.cart import Cart
from app.domain.exceptions import DomainException
from app.domain.services.article_stock_service import ArticleStockChecker


@pytest.fixture
def stock_checker_mock():
    checker = MagicMock(spec=ArticleStockChecker)
    checker.has_sufficient_stock.return_value = True
    return checker


@pytest.fixture
def empty_cart():
    return Cart.initialize(user_id="user-123")


def test_initialize_cart_creates_empty_cart(empty_cart):
    assert empty_cart.user_id == "user-123"
    assert empty_cart.is_empty is True
    assert len(empty_cart.get_items()) == 0


def test_add_item_increases_quantity_and_respects_stock(empty_cart, stock_checker_mock):
    empty_cart.add_item("art-1", 3, stock_checker_mock)

    items = empty_cart.get_items()
    assert len(items) == 1
    assert items[0].article_id == "art-1"
    assert items[0].quantity == 3
    stock_checker_mock.has_sufficient_stock.assert_called_once_with("art-1", 3)


def test_add_item_fails_if_insufficient_stock(empty_cart, stock_checker_mock):
    stock_checker_mock.has_sufficient_stock.return_value = False

    with pytest.raises(DomainException, match="Insufficient stock available"):
        empty_cart.add_item("art-1", 5, stock_checker_mock)


def test_add_item_enforces_maximum_business_limit(empty_cart, stock_checker_mock):
    empty_cart.add_item("art-1", 10, stock_checker_mock)

    with pytest.raises(DomainException, match="Cannot add more than 10 units"):
        empty_cart.add_item("art-1", 1, stock_checker_mock)


def test_change_item_quantity_updates_correctly(empty_cart, stock_checker_mock):
    empty_cart.add_item("art-1", 2, stock_checker_mock)
    empty_cart.change_item_quantity("art-1", 5, stock_checker_mock)

    items = empty_cart.get_items()
    assert items[0].quantity == 5


def test_remove_item_and_clear_cart(empty_cart, stock_checker_mock):
    empty_cart.add_item("art-1", 1, stock_checker_mock)
    empty_cart.add_item("art-2", 2, stock_checker_mock)

    empty_cart.remove_item("art-1")
    assert len(empty_cart.get_items()) == 1

    empty_cart.clear()
    assert empty_cart.is_empty is True
