from datetime import date
from dataclasses import dataclass
from app.domain.value_objects.email import Email
from app.domain.value_objects.shipping_address import ShippingAddress
from app.domain.value_objects.birth_date import BirthDate


@dataclass
class User:
    id: str
    first_name: str
    last_name: str
    email: Email
    birth_date: BirthDate
    password_hash: str
    shipping_address: ShippingAddress

    @classmethod
    def register(
        cls,
        id: str,
        first_name: str,
        last_name: str,
        email: Email,
        birth_date: BirthDate,
        password_hash: str,
        shipping_address: ShippingAddress,
    ):
        return cls(
            id=id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            birth_date=birth_date,
            password_hash=password_hash,
            shipping_address=shipping_address,
        )

    # -------------- Setters for updating user information --------------
    def update_shipping_address(self, new_address: ShippingAddress):
        self.shipping_address = new_address

    def change_password(self, new_password_hash: str):
        self.password_hash = new_password_hash

    def update_email(self, new_email: Email):
        self.email = new_email

    def update_first_name(self, new_first_name: str):
        self.first_name = new_first_name

    def update_last_name(self, new_last_name: str):
        self.last_name = new_last_name

    # -------------- Getters for retrieving user information --------------
    def get_email(self) -> Email:
        return self.email

    def get_birth_date(self) -> BirthDate:
        return self.birth_date

    def get_shipping_address(self) -> ShippingAddress:
        return self.shipping_address

    def get_id(self) -> str:
        return self.id

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
