import sqlite3
from typing import Optional
from app.application.ports.cart_repository import CartRepository
from app.domain.aggregates.cart import Cart
from app.infrastructure.repositories.mappers.cart_mapper import CartMapper


class SqliteCartRepository(CartRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                user_id TEXT PRIMARY KEY,
                items TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def save(self, cart: Cart) -> None:
        cursor = self.conn.cursor()
        db_record = CartMapper.to_persistence(cart)

        cursor.execute(
            """
                INSERT INTO carts (user_id, items)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    items=excluded.items
            """,
            db_record,
        )

        self.conn.commit()

    def find_by_user_id(self, user_id: str) -> Optional[Cart]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM carts WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return CartMapper.to_domain(row)

    def delete_by_user_id(self, user_id: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
        self.conn.commit()
