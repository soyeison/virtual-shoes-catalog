from app.application.ports.user_repository import UserRepository
from app.application.ports.password_hasher import PasswordHasher
from app.application.ports.token_generator import TokenGenerator
from app.domain.exceptions import InvalidCredentialsException


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        hasher: PasswordHasher,
        token_generator: TokenGenerator,
    ):
        self.user_repository = user_repository
        self.hasher = hasher
        self.token_generator = token_generator

    def execute(self, raw_email: str, plain_password: str):
        user = self.user_repository.find_by_email(raw_email)

        if not user:
            raise InvalidCredentialsException("Invalid email or password.")

        is_valid = self.hasher.verify(plain_password, user.password_hash)
        if not is_valid:
            raise InvalidCredentialsException("Invalid email or password.")

        token = self.token_generator.generate(user.id)
        return token
