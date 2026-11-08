import stripe
from app.domain.value_objects.price import Price
from app.application.ports.payment_gateway import GatewayResponse, PaymentGateway


class StripePaymentGateway(PaymentGateway):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.zero_decimal_currencies = ["COP", "CLP", "JPY", "KRW"]

    def _format_amount_for_stripe(self, price: Price) -> int:
        if price.currency.upper() in self.zero_decimal_currencies:
            return int(price.amount)
        return int(price.amount * 100)

    def process_charge(
        self, payment_id: str, amount: Price, payment_token: str
    ) -> GatewayResponse:
        try:
            strpe_amount = self._format_amount_for_stripe(amount)

            intent = stripe.PaymentIntent.create(
                amount=strpe_amount,
                currency=amount.currency.lower(),
                payment_method=payment_token,
                confirm=True,
                automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
                description=f"Charge for internal payment ID: {payment_id}",
                metadata={"internal_payment_id": payment_id},
            )

            if intent.status in ["succeeded", "requires_capture"]:
                return GatewayResponse(
                    is_successful=True, transaction_id=intent.id, error_message=None
                )
            else:
                return GatewayResponse(
                    is_successful=False,
                    transaction_id=intent.id,
                    error_message=f"Payment requires further action. Status: {intent.status}",
                )
        except stripe.CardError as e:
            err = e.error

            error_message = "Card was declined."
            transaction_id = None

            if err:
                error_message = err.message or error_message
                payment_intent = getattr(err, "payment_intent", None)
                if payment_intent:
                    transaction_id = getattr(payment_intent, "id", None)

            return GatewayResponse(
                is_successful=False,
                transaction_id=transaction_id,
                error_message=error_message,
            )
        except stripe.StripeError as e:
            return GatewayResponse(
                is_successful=False,
                transaction_id=None,
                error_message="Payment processing service is currently unavailable.",
            )
