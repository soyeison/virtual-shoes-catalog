from decimal import Decimal
import pytest
from app.domain.aggregates.order import Order, OrderItem, OrderStatus
from app.domain.aggregates.article import Price
from app.domain.exceptions import DomainException


def test_order_calculates_total_correctly():
    # Arrange
    item1 = OrderItem("novarun-shoe-1", 2, Price(Decimal("150.00"), "COP"))
    item2 = OrderItem("novarun-shoe-2", 1, Price(Decimal("100.00"), "COP"))

    # Act
    order = Order.create(order_id="ord-123", user_id="usr-1", items=[item1, item2])

    # Assert
    assert order.total_amount.amount == Decimal("400.00")
    assert order.total_amount.currency == "COP"
    assert order.status == OrderStatus.PENDING


def test_order_creation_fails_without_items():
    with pytest.raises(DomainException) as exc_info:
        Order.create(order_id="ord-1", user_id="usr-1", items=[])

    assert "at least one item" in str(exc_info.value)


def test_successful_payment_transition():
    item = OrderItem("item-1", 1, Price(Decimal("50.00"), "COP"))
    order = Order.create("ord-1", "usr-1", [item])

    order.pay()

    assert order.status == OrderStatus.PAID


def test_cannot_cancel_already_paid_order():
    item = OrderItem("item-1", 1, Price(Decimal("50.00"), "COP"))
    order = Order.create("ord-1", "usr-1", [item])
    order.pay()

    with pytest.raises(DomainException) as exc_info:
        order.cancel()

    assert "already been paid" in str(exc_info.value)
