import sqlite3
from datetime import date
from typing import Dict, Any
from app.domain.aggregates.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.shipping_address import ShippingAddress
from app.domain.value_objects.birth_date import BirthDate


class UserMapper:
    @staticmethod
    def to_domain(row: sqlite3.Row | Dict[str, Any]) -> User:
        email = Email(row["email"])
        shipping_address = ShippingAddress(
            street=row["street"],
            city=row["city"],
            zip_code=row["zip_code"],
            country=row["country"],
        )
        birth_date = BirthDate(date.fromisoformat(row["birth_date"]))

        return User(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=email,
            birth_date=birth_date,
            password_hash=row["password_hash"],
            shipping_address=shipping_address,
        )

    @staticmethod
    def to_persistence(user: User) -> tuple:
        return (
            user.id,
            user.first_name,
            user.last_name,
            user.birth_date.value,
            user.email.value,
            user.password_hash,
            user.shipping_address.street,
            user.shipping_address.city,
            user.shipping_address.zip_code,
            user.shipping_address.country,
        )
