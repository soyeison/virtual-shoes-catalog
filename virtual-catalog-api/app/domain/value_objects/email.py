import re
from dataclasses import dataclass
from app.domain.exceptions import DomainException


@dataclass
class Email:
    value: str

    def __post_init__(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise DomainException("Invalid email format.")
