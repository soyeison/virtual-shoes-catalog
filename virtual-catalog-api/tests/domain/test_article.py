import pytest
from decimal import Decimal
from app.domain.aggregates.article import Article, Stock, Price, ImageURL
from app.domain.exceptions import DomainException


@pytest.fixture
def base_article():
    return Article.create(
        id="art-123",
        name="Zapatos Nike Air Max",
        description="Algodón 100%",
        initial_stock=Stock(20),
        initial_price=Price(Decimal("45000.00"), "COP"),
    )


def test_article_creation_assigns_correct_values(base_article):
    assert base_article.id == "art-123"
    assert base_article.name == "Zapatos Nike Air Max"
    assert base_article.get_stock().value == 20
    assert len(base_article.get_image_urls()) == 0


def test_article_cannot_be_created_with_empty_name():
    with pytest.raises(DomainException, match="Article name cannot be empty"):
        Article.create("id", "   ", "desc", Stock(1), Price(Decimal("10"), "COP"))


def test_attach_image_respects_maximum_limit_of_five(base_article):
    for i in range(5):
        base_article.attach_image(ImageURL(f"http://localhost/img{i}.jpg"))

    assert len(base_article.get_image_urls()) == 5

    with pytest.raises(
        DomainException, match="Cannot attach more than 5 images to an article"
    ):
        base_article.attach_image(ImageURL("http://localhost/img6.jpg"))
