from datetime import date
from dataclasses import dataclass
from app.domain.exceptions import DomainException


@dataclass
class BirthDate:
    value: date

    def __post_init__(self):
        if self.value > date.today():
            raise DomainException("Birth date cannot be in the future.")

        years_difference = date.today().year - self.value.year
        if years_difference < 18:
            raise DomainException("User must be at least 18 years old.")
