import pytest
from datetime import date
from app.domain.aggregates.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.shipping_address import ShippingAddress
from app.domain.value_objects.birth_date import BirthDate
from app.domain.exceptions import DomainException


def test_user_registry_generate_entity_correctly():
    email = Email("test@test.com")
    address = ShippingAddress("Calle 13", "Medellín", "05000", "Colombia")
    birth_date = BirthDate(date(1990, 1, 1))

    user = User.register(
        id="123",
        first_name="Jhon",
        last_name="Doe",
        birth_date=birth_date,
        password_hash="hashed_password",
        email=email,
        shipping_address=address,
    )

    assert user.id == "123"
    assert user.first_name == "Jhon"
    assert user.last_name == "Doe"
    assert user.birth_date == birth_date
    assert user.password_hash == "hashed_password"
    assert user.email == email
    assert user.shipping_address == address
