from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod
from app.domain.value_objects.price import Price


@dataclass
class GatewayResponse:
    is_successful: bool
    transaction_id: Optional[str]
    error_message: Optional[str]


class PaymentGateway(ABC):
    @abstractmethod
    def process_charge(
        self, payment_id: str, amount: Price, payment_token: str
    ) -> GatewayResponse:
        pass
