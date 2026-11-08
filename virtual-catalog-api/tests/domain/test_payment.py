from decimal import Decimal
import pytest
from app.domain.aggregates.payment import Payment, PaymentStatus
from app.domain.aggregates.article import Price
from app.domain.exceptions import DomainException


def test_payment_initializes_as_pending():
    payment = Payment.initialize("pay-1", "ord-123", Price(Decimal("150.00"), "COP"))

    assert payment.status == PaymentStatus.PENDING
    assert payment.amount.amount == Decimal("150.00")


def test_mark_payment_as_successful():
    payment = Payment.initialize("pay-1", "ord-123", Price(Decimal("150.00"), "COP"))
    payment.mark_as_successful()

    assert payment.status == PaymentStatus.COMPLETED


def test_cannot_mark_failed_payment_as_successful():
    payment = Payment.initialize("pay-1", "ord-123", Price(Decimal("150.00"), "COP"))
    payment.mark_as_failed()

    # Intento de vulneración: tratar de pasar a SUCCESS un pago que ya falló
    with pytest.raises(DomainException) as exc_info:
        payment.mark_as_successful()

    assert "Cannot mark as successful" in str(exc_info.value)
