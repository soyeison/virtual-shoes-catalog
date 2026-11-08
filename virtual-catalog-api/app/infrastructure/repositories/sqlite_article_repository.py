import sqlite3
from typing import Optional, List, Tuple
from app.application.ports.article_repository import ArticleRepository
from app.application.queries.article_criteria import ArticleCriteria
from app.domain.aggregates.article import Article
from app.infrastructure.repositories.mappers.article_mapper import ArticleMapper


class SqliteArticleRepository(ArticleRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                stock INTEGER NOT NULL,
                price_amount TEXT NOT NULL,
                price_currency TEXT NOT NULL,
                image_urls TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def create(self, article: Article) -> None:
        cursor = self.conn.cursor()
        db_record = ArticleMapper.to_persistence(article)

        cursor.execute(
            """
            INSERT INTO articles (id, name, description, stock, price_amount, price_currency, image_urls)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            db_record,
        )
        self.conn.commit()

    def update(self, article: Article) -> None:
        cursor = self.conn.cursor()
        db_record = ArticleMapper.to_persistence(article)
        update_values = db_record[1:] + (db_record[0],)

        cursor.execute(
            """
            UPDATE articles 
            SET name = ?, 
                description = ?, 
                stock = ?, 
                price_amount = ?, 
                price_currency = ?, 
                image_urls = ?
            WHERE id = ?
        """,
            update_values,
        )
        self.conn.commit()

    def find_by_id(self, article_id: str) -> Optional[Article]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return ArticleMapper.to_domain(row)

    def find_all(self) -> List[Article]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM articles")
        rows = cursor.fetchall()

        return [ArticleMapper.to_domain(row) for row in rows]

    def search(self, criteria: ArticleCriteria) -> Tuple[List[Article], int]:
        cursor = self.conn.cursor()

        # 1. Build the dynamic WHERE clauses
        where_clauses = ["1=1"]
        params = []

        if criteria.name_contains:
            where_clauses.append("name LIKE ?")
            params.append(f"%{criteria.name_contains}%")

        if criteria.min_price is not None:
            where_clauses.append("CAST(price_amount AS REAL) >= ?")
            params.append(criteria.min_price)

        if criteria.max_price is not None:
            where_clauses.append("CAST(price_amount AS REAL) <= ?")
            params.append(criteria.max_price)

        where_sql = " AND ".join(where_clauses)

        # 2. Execute the COUNT query first
        count_query = f"SELECT COUNT(*) FROM articles WHERE {where_sql}"
        cursor.execute(count_query, params)
        total_records = cursor.fetchone()[0]

        # 3. Build the final SELECT query with ordering and pagination
        select_query = f"SELECT * FROM articles WHERE {where_sql}"

        if criteria.sort_by == "price_asc":
            select_query += " ORDER BY CAST(price_amount AS REAL) ASC"
        elif criteria.sort_by == "price_desc":
            select_query += " ORDER BY CAST(price_amount AS REAL) DESC"
        else:
            select_query += " ORDER BY id DESC"

        select_query += " LIMIT ? OFFSET ?"
        # We append limit and offset parameters specifically for the select query
        select_params = params + [criteria.limit, criteria.offset]

        # 4. Execute and map the results
        cursor.execute(select_query, select_params)
        rows = cursor.fetchall()

        articles = [ArticleMapper.to_domain(row) for row in rows]

        return articles, len(articles)
