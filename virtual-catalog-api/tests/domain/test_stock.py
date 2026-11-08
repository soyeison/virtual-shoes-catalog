import pytest
from app.domain.value_objects.stock import Stock
from app.domain.exceptions import DomainException


def test_stock_cannot_be_negative():
    with pytest.raises(DomainException, match="Stock value cannot be negative"):
        Stock(-1)


def test_stock_decrease_success_returns_new_instance():
    initial_stock = Stock(10)
    new_stock = initial_stock.decrease(4)

    assert new_stock.value == 6
    assert initial_stock.value == 10  # Ensures immutability


def test_stock_decrease_insufficient_raises_exception():
    stock = Stock(5)
    with pytest.raises(DomainException, match="Cannot decrease stock below zero"):
        stock.decrease(6)
