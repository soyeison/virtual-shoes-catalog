import pytest
from app.domain.value_objects.shipping_address import ShippingAddress
from app.domain.exceptions import DomainException


def test_shipping_address_is_valid():
    address = ShippingAddress(
        street="Calle 13", city="Medellín", zip_code="05000", country="Colombia"
    )
    assert address.street == "Calle 13"
    assert address.city == "Medellín"
    assert address.zip_code == "05000"
    assert address.country == "Colombia"


def test_shipping_address_throw_exception():
    with pytest.raises(DomainException, match="Invalid zip code format."):
        ShippingAddress(
            street="Calle 13",
            city="Medellín",
            zip_code="invalid-zip",
            country="Colombia",
        )


def test_shipping_address_throw_exception_empty_fields():
    with pytest.raises(DomainException, match="All address fields must be provided."):
        ShippingAddress(
            street="",
            city="Medellín",
            zip_code="05000",
            country="Colombia",
        )

    with pytest.raises(DomainException, match="All address fields must be provided."):
        ShippingAddress(
            street="Calle 13",
            city="",
            zip_code="05000",
            country="Colombia",
        )

    with pytest.raises(DomainException, match="All address fields must be provided."):
        ShippingAddress(
            street="Calle 13",
            city="Medellín",
            zip_code="05000",
            country="",
        )
