import sqlite3
from app.domain.aggregates.user import User
from app.infrastructure.repositories.mappers.user_maper import UserMapper
from app.application.ports.user_repository import UserRepository


class SqliteUserRepository(UserRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birth_date DATE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                street TEXT NOT NULL,
                city TEXT NOT NULL,
                zip_code TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def save(self, user: User):
        cursor = self.conn.cursor()

        db_record = UserMapper.to_persistence(user)

        cursor.execute(
            """
            INSERT INTO users (id, first_name, last_name, birth_date, email, password_hash, street, city, zip_code, country)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            db_record,
        )

        self.conn.commit()

    def find_by_id(self, user_id: str) -> User | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return UserMapper.to_domain(row)

    def find_by_email(self, email: str) -> User | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()

        if not row:
            return None

        return UserMapper.to_domain(row)
