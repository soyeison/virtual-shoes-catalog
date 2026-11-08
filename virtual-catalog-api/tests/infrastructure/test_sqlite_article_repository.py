import pytest
import sqlite3
from decimal import Decimal
from app.application.queries.article_criteria import ArticleCriteria
from app.domain.aggregates.article import Article, Stock, Price, ImageURL
from app.infrastructure.repositories.sqlite_article_repository import (
    SqliteArticleRepository,
)


@pytest.fixture
def populated_repo():
    connection = sqlite3.connect(":memory:")
    repo = SqliteArticleRepository(connection)

    test_articles = [
        Article(
            id="art-1",
            name="Zapatos Nike Air Max",
            description="Zapatos de deporte",
            stock=Stock(10),
            price=Price(Decimal("150000.00"), "COP"),
            image_urls=[ImageURL("http://localhost:9000/catalogo-images/teclado.jpg")],
        ),
        Article(
            id="art-2",
            name="Zapatos Adidas Ultraboost",
            description="Zapatos de running",
            stock=Stock(5),
            price=Price(Decimal("1200000.00"), "COP"),
            image_urls=[],
        ),
        Article(
            id="art-3",
            name="Zapatos Puma RS-X",
            description="Zapatos de basketball",
            stock=Stock(25),
            price=Price(Decimal("450000.00"), "COP"),
            image_urls=[ImageURL("http://localhost:9000/catalogo-images/mouse.jpg")],
        ),
    ]

    for article in test_articles:
        repo.create(article)

    yield repo

    connection.close()


def test_search_without_criteria_returns_all_articles(populated_repo):
    criteria = ArticleCriteria()
    _, results_number = populated_repo.search(criteria)
    assert results_number == 3


def test_search_by_partial_name(populated_repo):
    criteria = ArticleCriteria(name_contains="Puma")
    results, results_number = populated_repo.search(criteria)
    assert results_number == 1
    assert results[0].id == "art-3"
    assert results[0].name == "Zapatos Puma RS-X"


def test_search_pagination_with_limit_and_offset(populated_repo):
    criteria = ArticleCriteria(name_contains="Zapatos", limit=2, offset=1)
    results, results_number = populated_repo.search(criteria)

    assert results_number == 2
    assert results[0].id == "art-2"
    assert results[1].id == "art-1"


def test_search_by_price_range(populated_repo):
    criteria = ArticleCriteria(min_price=100000.0, max_price=500000.0)

    # Act
    results, results_number = populated_repo.search(criteria)

    # Assert
    assert results_number == 2
    ids_results = [art.id for art in results]
    assert "art-1" in ids_results  # Zapatos Nike Air Max (150k)
    assert "art-3" in ids_results  # Zapatos Puma RS-X (450k)


def test_search_by_price_sorting(populated_repo):
    # Arrange
    criteria = ArticleCriteria(sort_by="price_asc")

    # Act
    results, results_number = populated_repo.search(criteria)

    # Assert
    assert results_number == 3
    assert results[0].id == "art-1"  # Zapatos Nike Air Max
    assert results[1].id == "art-3"  # Zapatos Puma RS-X
    assert results[2].id == "art-2"  # Zapatos Adidas Ultraboost


def test_search_by_price_desc_sorting(populated_repo):
    # Arrange
    criteria = ArticleCriteria(sort_by="price_desc")

    # Act
    results, results_number = populated_repo.search(criteria)

    # Assert
    assert results_number == 3
    assert results[0].id == "art-2"
    assert results[1].id == "art-3"
    assert results[2].id == "art-1"


def test_search_with_multiple_criteria(populated_repo):
    # Arrange
    # Buscamos un artículo que tenga "Adidas" en el nombre Y cueste más de 1,200,000 COP
    criteria = ArticleCriteria(name_contains="Adidas", min_price=1200000.0)

    # Act
    results, results_number = populated_repo.search(criteria)

    # Assert
    assert results_number == 1
    assert results[0].id == "art-2"
