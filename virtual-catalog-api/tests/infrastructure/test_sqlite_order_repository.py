import sqlite3
from decimal import Decimal
import pytest
from app.domain.aggregates.order import Order, OrderItem
from app.domain.aggregates.article import Price
from app.infrastructure.repositories.sqlite_order_repository import (
    SqliteOrderRepository,
)


@pytest.fixture
def in_memory_db():
    """Configura una base de datos efímera para las pruebas."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_save_and_retrieve_order(in_memory_db):
    # Arrange
    repo = SqliteOrderRepository(in_memory_db)

    item = OrderItem("novarun-shoe-model-x", 1, Price(Decimal("250.00"), "COP"))
    order = Order.create(order_id="ord-999", user_id="usr-555", items=[item])

    # Act: Guardamos la orden en el SQLite en memoria
    repo.save(order)

    # Act: Recuperamos la orden mediante un nuevo query
    retrieved_order = repo.find_by_id("ord-999")

    # Assert
    assert retrieved_order is not None
    assert retrieved_order.id == "ord-999"
    assert retrieved_order.user_id == "usr-555"
    assert retrieved_order.status.value == "PENDING"
    assert retrieved_order.total_amount.amount == Decimal("250.00")

    # Verificamos que el JSON se serializó y deserializó correctamente
    items = retrieved_order.get_items()
    assert len(items) == 1
    assert items[0].article_id == "novarun-shoe-model-x"


def test_update_order_status_upsert(in_memory_db):
    # Arrange
    repo = SqliteOrderRepository(in_memory_db)
    item = OrderItem("item-1", 1, Price(Decimal("10.00"), "COP"))
    order = Order.create("ord-888", "usr-1", [item])
    repo.save(order)

    # Act: Cambiamos el estado en memoria y volvemos a guardar (Upsert)
    order.pay()
    repo.save(order)

    # Assert
    updated_order = repo.find_by_id("ord-888")
    assert updated_order is not None
    assert updated_order.status.value == "PAID"
