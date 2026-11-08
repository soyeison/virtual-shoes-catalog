from dataclasses import dataclass
from app.domain.exceptions import DomainException


@dataclass
class ShippingAddress:
    street: str
    city: str
    zip_code: str
    country: str

    def __post_init__(self):
        if not self.street or not self.city or not self.zip_code or not self.country:
            raise DomainException("All address fields must be provided.")

        if not self.zip_code.isdigit() or len(self.zip_code) < 5:
            raise DomainException("Invalid zip code format.")
