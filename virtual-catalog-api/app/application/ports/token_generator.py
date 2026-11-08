from abc import ABC, abstractmethod


class TokenGenerator(ABC):
    @abstractmethod
    def generate(self, user_id: str) -> str:
        pass
