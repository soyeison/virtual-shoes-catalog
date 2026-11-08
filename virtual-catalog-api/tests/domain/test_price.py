import pytest
from decimal import Decimal
from app.domain.value_objects.price import Price
from app.domain.exceptions import DomainException


def test_price_cannot_be_negative():
    with pytest.raises(DomainException, match="Price amount cannot be negative"):
        Price(Decimal("-100.00"), "COP")


def test_price_currency_must_be_iso_4217():
    with pytest.raises(DomainException, match="Currency must be a 3-letter code"):
        Price(Decimal("5000.00"), "PESOS")


def test_add_prices_with_different_currency_raises_exception():
    price_cop = Price(Decimal("50000"), "COP")
    price_usd = Price(Decimal("10"), "USD")

    with pytest.raises(
        DomainException, match="Cannot add prices with different currencies"
    ):
        price_cop.add(price_usd)
