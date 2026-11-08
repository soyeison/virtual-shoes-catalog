import sqlite3
from typing import List, Optional
from app.application.ports.payment_repository import PaymentRepository
from app.domain.aggregates.payment import Payment
from app.infrastructure.repositories.mappers.payment_mapper import PaymentMapper


class SqlitePaymentRepository(PaymentRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                amount TEXT NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id)
        """)
        self.conn.commit()

    def save(self, payment: Payment) -> None:
        cursor = self.conn.cursor()
        db_record = PaymentMapper.to_persistence(payment)

        cursor.execute(
            """
            INSERT INTO payments (id, order_id, amount, currency, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status=excluded.status,
                updated_at=excluded.updated_at
        """,
            db_record,
        )

        self.conn.commit()

    def find_by_id(self, payment_id: str) -> Optional[Payment]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        row = cursor.fetchone()
        return PaymentMapper.to_domain(row) if row else None

    def find_by_order_id(self, order_id: str) -> List[Payment]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM payments WHERE order_id = ? ORDER BY created_at DESC",
            (order_id,),
        )
        rows = cursor.fetchall()
        return [PaymentMapper.to_domain(row) for row in rows]
