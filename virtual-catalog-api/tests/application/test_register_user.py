import pytest
from unittest.mock import MagicMock
from app.application.use_cases.register_user import RegisterUserUseCase


@pytest.fixture
def mock_user_repository():
    return MagicMock()


@pytest.fixture
def mock_hasher():
    hasher = MagicMock()
    hasher.hash.return_value = "hashed_password"
    return hasher


def test_save_new_user(mock_user_repository, mock_hasher):
    mock_user_repository.find_by_email.return_value = None
    use_case = RegisterUserUseCase(
        user_repository=mock_user_repository, hasher=mock_hasher
    )

    new_user = use_case.execute(
        first_name="John",
        last_name="Doe",
        raw_email="john.doe@example.com",
        birth_date="1990-01-01",
        password="password123",
        city="New York",
        street="123 Main St",
        country="USA",
        postal_code="10001",
    )

    assert new_user is not None
    mock_user_repository.find_by_email.assert_called_once_with("john.doe@example.com")
    mock_user_repository.save.assert_called_once()


def test_register_user_with_existing_email(mock_user_repository, mock_hasher):
    mock_user_repository.find_by_email.return_value = True
    use_case = RegisterUserUseCase(
        user_repository=mock_user_repository, hasher=mock_hasher
    )

    with pytest.raises(ValueError) as exc_info:
        use_case.execute(
            first_name="John",
            last_name="Doe",
            raw_email="john.doe@example.com",
            birth_date="1990-01-01",
            password="password123",
            city="New York",
            street="123 Main St",
            country="USA",
            postal_code="10001",
        )
    assert str(exc_info.value) == "A user with this email already exists."
