import pytest
from app.domain.value_objects.email import Email
from app.domain.exceptions import DomainException


def test_email_is_valid():
    email = Email("test@poligran.edu.co")
    assert email.value == "test@poligran.edu.co"


def test_email_throw_exception():
    with pytest.raises(DomainException, match="Invalid email format."):
        Email("invalid-email")
