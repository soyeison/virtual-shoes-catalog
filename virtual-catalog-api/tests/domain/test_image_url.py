import pytest
from app.domain.aggregates.article import ImageURL
from app.domain.exceptions import DomainException


def test_invalid_image_url_raises_exception():
    with pytest.raises(DomainException, match="Invalid URL format"):
        ImageURL("local_file.jpg")
