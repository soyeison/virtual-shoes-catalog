import sqlite3
from typing import List, Optional
from app.application.ports.order_repository import OrderRepository
from app.domain.aggregates.order import Order
from app.infrastructure.repositories.mappers.order_mapper import OrderMapper


class SqliteOrderRepository(OrderRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                items TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)
        """)
        self.conn.commit()

    def save(self, order: Order) -> None:
        cursor = self.conn.cursor()
        db_record = OrderMapper.to_persistence(order)

        cursor.execute(
            """
            INSERT INTO orders (id, user_id, status, created_at, items)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status=excluded.status
        """,
            db_record,
        )

        self.conn.commit()

    def find_by_id(self, order_id: str) -> Optional[Order]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return OrderMapper.to_domain(row)

    def find_by_user_id(self, user_id: str) -> List[Order]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        rows = cursor.fetchall()

        return [OrderMapper.to_domain(row) for row in rows]
