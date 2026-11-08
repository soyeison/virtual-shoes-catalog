import sqlite3
import json
from decimal import Decimal
from typing import Dict, Any
from app.domain.aggregates.article import Article, Stock, Price, ImageURL


class ArticleMapper:
    @staticmethod
    def to_domain(row: sqlite3.Row | Dict[str, Any]) -> Article:
        stock = Stock(value=row["stock"])

        price = Price(
            amount=Decimal(str(row["price_amount"])), currency=row["price_currency"]
        )

        urls_data = json.loads(row["image_urls"]) if row["image_urls"] else []
        image_urls = [ImageURL(url) for url in urls_data]

        return Article(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            stock=stock,
            price=price,
            image_urls=image_urls,
        )

    @staticmethod
    def to_persistence(article: Article) -> tuple:
        urls_list = [img.url for img in article.get_image_urls()]
        urls_json = json.dumps(urls_list)

        return (
            article.id,
            article.name,
            article.description,
            article.get_stock().value,
            str(article.get_price().amount),  # Guardamos el Decimal como texto
            article.get_price().currency,
            urls_json,
        )
