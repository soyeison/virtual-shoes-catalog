import pytest
import sqlite3
from app.domain.aggregates.cart import Cart, CartItem
from app.infrastructure.repositories.sqlite_cart_repository import SqliteCartRepository


@pytest.fixture
def sqlite_cart_repo():
    connection = sqlite3.connect(":memory:")
    repo = SqliteCartRepository(connection)
    yield repo
    connection.close()


def test_save_and_find_by_user_id(sqlite_cart_repo):
    # Arrange
    cart = Cart.initialize("user-99")
    # Using the backdoor just for testing persistence setup
    cart._items = {"art-1": CartItem("art-1", 2), "art-2": CartItem("art-2", 5)}

    # Act
    sqlite_cart_repo.save(cart)
    retrieved_cart = sqlite_cart_repo.find_by_user_id("user-99")

    # Assert
    assert retrieved_cart is not None
    assert retrieved_cart.user_id == "user-99"

    items = retrieved_cart.get_items()
    assert len(items) == 2
    # Verify the JSON serialization preserved the data correctly
    art_1 = next(i for i in items if i.article_id == "art-1")
    assert art_1.quantity == 2


def test_save_updates_existing_record_using_upsert(sqlite_cart_repo):
    # Arrange
    cart = Cart.initialize("user-100")
    cart._items = {"art-1": CartItem("art-1", 1)}
    sqlite_cart_repo.save(cart)  # Initial insert

    # Act
    # Simulate user adding another item later
    cart._items["art-2"] = CartItem("art-2", 3)
    sqlite_cart_repo.save(cart)  # Upsert

    # Assert
    retrieved_cart = sqlite_cart_repo.find_by_user_id("user-100")
    assert len(retrieved_cart.get_items()) == 2


def test_delete_by_user_id(sqlite_cart_repo):
    # Arrange
    cart = Cart.initialize("user-101")
    sqlite_cart_repo.save(cart)

    # Act
    sqlite_cart_repo.delete_by_user_id("user-101")
    retrieved_cart = sqlite_cart_repo.find_by_user_id("user-101")

    # Assert
    assert retrieved_cart is None
