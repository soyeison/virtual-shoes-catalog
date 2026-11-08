import pytest
import sqlite3
from datetime import date
from app.domain.aggregates.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.shipping_address import ShippingAddress
from app.domain.value_objects.birth_date import BirthDate
from app.infrastructure.repositories.sqlite_user_repository import SqliteUserRepository


@pytest.fixture
def sqlite_user_repository():
    # Setup: Se ejecuta ANTES de la prueba
    conn = sqlite3.connect(":memory:")
    repo = SqliteUserRepository(conn)
    yield repo  # Entrega el repo a la prueba

    # Teardown: Se ejecuta DESPUÉS de la prueba (limpieza)
    conn.close()


def test_save_and_find_user_correctly(sqlite_user_repository):
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

    sqlite_user_repository.save(user)
    print("User saved to the repository.")
    user_finded = sqlite_user_repository.find_by_email("test@test.com")

    assert user_finded is not None
    assert user_finded.id == user.id


def search_user_not_found(sqlite_user_repository):
    user_finded = sqlite_user_repository.find_by_email("test@test.com")
    assert user_finded is None
