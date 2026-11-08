from app.domain.aggregates.order import Order
from app.application.ports.order_repository import OrderRepository
from app.domain.exceptions import DomainException


class GetOrderUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order_id: str) -> Order:
        order = self.order_repository.find_by_id(order_id)

        if not order:
            raise DomainException(f"Order with ID {order_id} not found.")

        return order
