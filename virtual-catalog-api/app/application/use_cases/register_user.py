import uuid
from datetime import datetime
from app.domain.aggregates.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.birth_date import BirthDate
from app.domain.value_objects.shipping_address import ShippingAddress
from app.application.ports.user_repository import UserRepository
from app.application.ports.password_hasher import PasswordHasher


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository, hasher: PasswordHasher):
        self.user_repository = user_repository
        self.hasher = hasher

    def execute(
        self,
        first_name: str,
        last_name: str,
        raw_email: str,
        birth_date: str,
        password: str,
        city: str,
        street: str,
        country: str,
        postal_code: str,
    ):
        # Verificar primero si el usuario ya existe con ese correo electrónico
        existing_user = self.user_repository.find_by_email(raw_email)

        if existing_user:
            raise ValueError("A user with this email already exists.")

        # Registrar el usuario
        email = Email(raw_email)
        birth_date_obj = BirthDate(datetime.strptime(birth_date, "%Y-%m-%d").date())
        shipping_address = ShippingAddress(
            street=street, city=city, country=country, zip_code=postal_code
        )
        new_user = User.register(
            id=str(uuid.uuid4()),
            first_name=first_name,
            last_name=last_name,
            email=email,
            birth_date=birth_date_obj,
            password_hash=self.hasher.hash(password),
            shipping_address=shipping_address,
        )

        self.user_repository.save(new_user)
        return new_user.id
