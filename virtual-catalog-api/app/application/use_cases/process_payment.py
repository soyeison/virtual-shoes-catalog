import uuid
from app.domain.aggregates.payment import Payment
from app.application.ports.payment_gateway import PaymentGateway
from app.application.ports.payment_repository import PaymentRepository
from app.application.ports.order_repository import OrderRepository
from app.domain.exceptions import DomainException


class ProcessPaymentUseCase:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        payment_gateway: PaymentGateway,
        order_repository: OrderRepository,
    ):
        self.payment_gateway = payment_gateway
        self.payment_repository = payment_repository
        self.order_repository = order_repository

    def execute(self, order_id: str, payment_token: str) -> Payment:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise DomainException(f"Order {order_id} not found")

        payment_id = f"pay-{uuid.uuid4().hex[:8]}"
        payment = Payment.initialize(
            payment_id=payment_id, order_id=order.id, amount=order.total_amount
        )

        self.payment_repository.save(payment)

        # Request the external charge via the Gateway Port
        gateway_response = self.payment_gateway.process_charge(
            payment_id=payment.id, amount=payment.amount, payment_token=payment_token
        )

        if gateway_response.is_successful:
            # Transition payment to SUCCESS
            payment.mark_as_successful()
            self.payment_repository.save(payment)

            # Transition order to PAID and persist
            order.pay()
            self.order_repository.save(order)
        else:
            payment.mark_as_failed()
            self.payment_repository.save(payment)

            raise DomainException(
                f"Payment failed: {gateway_response.error_message or 'Declined by bank'}"
            )

        return payment
