import pytest
from unittest.mock import MagicMock
from app.application.use_cases.login_user import LoginUserUseCase
from app.domain.exceptions import InvalidCredentialsException


@pytest.fixture
def mock_user_repository():
    return MagicMock()


@pytest.fixture
def mock_hasher():
    hasher = MagicMock()
    hasher.hash.return_value = "hashed_password"
    return hasher


@pytest.fixture
def mock_token_generator():
    token_generator = MagicMock()
    token_generator.generate.return_value = "fake_token"
    return token_generator


def test_login_user_success(mock_user_repository, mock_hasher, mock_token_generator):
    mock_user_repository.find_by_email.return_value = MagicMock(
        id=1, password_hash="hashed_password"
    )
    mock_hasher.verify.return_value = True

    use_case = LoginUserUseCase(
        user_repository=mock_user_repository,
        hasher=mock_hasher,
        token_generator=mock_token_generator,
    )

    token = use_case.execute(raw_email="test@test.com", plain_password="password123")
    assert token == "fake_token"


def test_login_user_invalid_email(
    mock_user_repository, mock_hasher, mock_token_generator
):
    mock_user_repository.find_by_email.return_value = None

    use_case = LoginUserUseCase(
        user_repository=mock_user_repository,
        hasher=mock_hasher,
        token_generator=mock_token_generator,
    )

    with pytest.raises(InvalidCredentialsException) as exc_info:
        use_case.execute(raw_email="nonexistent@test.com", plain_password="password123")
    assert str(exc_info.value) == "Invalid email or password."


def test_login_user_invalid_password(
    mock_user_repository, mock_hasher, mock_token_generator
):
    mock_user_repository.find_by_email.return_value = MagicMock(
        id=1, password_hash="hashed_password"
    )
    mock_hasher.verify.return_value = False

    use_case = LoginUserUseCase(
        user_repository=mock_user_repository,
        hasher=mock_hasher,
        token_generator=mock_token_generator,
    )

    with pytest.raises(InvalidCredentialsException) as exc_info:
        use_case.execute(raw_email="test@test.com", plain_password="wrong_password")
    assert str(exc_info.value) == "Invalid email or password."
