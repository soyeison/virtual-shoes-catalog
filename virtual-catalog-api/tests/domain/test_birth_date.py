import pytest
from datetime import date
from app.domain.value_objects.birth_date import BirthDate
from app.domain.exceptions import DomainException


def test_birth_date_is_valid():
    birth_date = BirthDate(date(1990, 1, 1))
    assert birth_date.value == date(1990, 1, 1)


def test_birth_date_throw_exception_future_date():
    future_date = date.today().replace(year=date.today().year + 1)
    with pytest.raises(DomainException, match="Birth date cannot be in the future."):
        BirthDate(future_date)


def test_birth_date_throw_exception_underage():
    underage_date = date.today().replace(year=date.today().year - 17)
    with pytest.raises(DomainException, match="User must be at least 18 years old."):
        BirthDate(underage_date)
