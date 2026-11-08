import sqlite3
from decimal import Decimal
import pytest
from app.domain.aggregates.payment import Payment, PaymentStatus
from app.domain.aggregates.article import Price
from app.infrastructure.repositories.sqlite_payment_repository import (
    SqlitePaymentRepository,
)


@pytest.fixture
def in_memory_db():
    """Configures an ephemeral SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_save_and_retrieve_payment(in_memory_db):
    # Arrange
    repo = SqlitePaymentRepository(in_memory_db)
    amount = Price(Decimal("150.50"), "COP")
    payment = Payment.initialize("pay-123", "ord-456", amount)

    # Act
    repo.save(payment)
    retrieved_payment = repo.find_by_id("pay-123")

    # Assert
    assert retrieved_payment is not None
    assert retrieved_payment.id == "pay-123"
    assert retrieved_payment.order_id == "ord-456"
    assert retrieved_payment.status == PaymentStatus.PENDING

    # Verify the Price Value Object was flattened and rebuilt correctly
    assert retrieved_payment.amount.amount == Decimal("150.50")
    assert retrieved_payment.amount.currency == "COP"


def test_update_payment_status_upsert(in_memory_db):
    # Arrange
    repo = SqlitePaymentRepository(in_memory_db)
    amount = Price(Decimal("50.00"), "COP")
    payment = Payment.initialize("pay-789", "ord-999", amount)
    repo.save(payment)

    # Act: Simulate a successful response from the Gateway
    payment.mark_as_successful()
    repo.save(payment)  # Upsert

    # Assert: Verify the database reflects the new status
    updated_payment = repo.find_by_id("pay-789")
    assert updated_payment is not None
    assert updated_payment.status == PaymentStatus.COMPLETED
    # Ensure the timestamp was actually updated during the domain logic
    assert updated_payment.updated_at >= updated_payment.created_at


def test_find_by_order_id_returns_multiple_attempts(in_memory_db):
    # Arrange
    repo = SqlitePaymentRepository(in_memory_db)
    amount = Price(Decimal("100.00"), "COP")

    # Simulate a user trying to pay, failing, and trying again
    failed_attempt = Payment.initialize("pay-fail-1", "ord-abc", amount)
    failed_attempt.mark_as_failed()
    repo.save(failed_attempt)

    successful_attempt = Payment.initialize("pay-success-2", "ord-abc", amount)
    successful_attempt.mark_as_successful()
    repo.save(successful_attempt)

    # Act
    payment_history = repo.find_by_order_id("ord-abc")

    # Assert
    assert len(payment_history) == 2

    # Verify both IDs are present in the retrieved list
    retrieved_ids = [p.id for p in payment_history]
    assert "pay-fail-1" in retrieved_ids
    assert "pay-success-2" in retrieved_ids
