import pytest
from app.domain.aggregates.cart import CartItem
from app.domain.exceptions import DomainException


def test_cart_item_cannot_have_zero_or_negative_quantity():
    with pytest.raises(DomainException, match="Quantity must be at least 1"):
        CartItem(article_id="art-1", quantity=0)


def test_cart_item_change_quantity_returns_new_instance():
    item = CartItem(article_id="art-1", quantity=2)
    new_item = item.change_quantity(5)

    assert new_item.quantity == 5
    assert new_item.article_id == "art-1"
    assert item.quantity == 2  # Immutability preserved
