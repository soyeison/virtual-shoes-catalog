import uuid
from app.domain.value_objects.price import Price
from app.application.ports.payment_gateway import PaymentGateway, GatewayResponse


class MockPaymentGateway(PaymentGateway):
    def process_charge(
        self, payment_id: str, amount: Price, payment_token: str
    ) -> GatewayResponse:
        transaction_id = f"txn_mock_{uuid.uuid4().hex[:12]}"

        if payment_token == "tok_declined":
            return GatewayResponse(
                is_successful=False,
                transaction_id=transaction_id,
                error_message="Card declined by the issuing bank.",
            )

        elif payment_token == "tok_insufficient_funds":
            return GatewayResponse(
                is_successful=False,
                transaction_id=transaction_id,
                error_message="Insufficient funds.",
            )

        elif payment_token == "tok_timeout":
            return GatewayResponse(
                is_successful=False,
                transaction_id=None,
                error_message="Gateway timeout. Please try again later.",
            )

        return GatewayResponse(
            is_successful=True, transaction_id=transaction_id, error_message=None
        )
