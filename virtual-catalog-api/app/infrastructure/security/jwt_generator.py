import jwt
from datetime import datetime, timedelta, timezone
from app.application.ports.token_generator import TokenGenerator


class JwtTokenGenerator(TokenGenerator):
    def __init__(
        self, secret_key: str, algorithm: str = "HS256", expiration_minutes: int = 60
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_minutes = expiration_minutes

    def generate(self, user_id: int) -> str:
        payload = {
            "sub": user_id,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=self.expiration_minutes),
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
