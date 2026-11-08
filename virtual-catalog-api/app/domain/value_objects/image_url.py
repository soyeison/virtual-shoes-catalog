import urllib.parse
from dataclasses import dataclass
from app.domain.exceptions import DomainException


@dataclass
class ImageURL:
    url: str

    def __post_init__(self):
        if not self.url:
            raise DomainException("Image URL cannot be empty")

        parsed = urllib.parse.urlparse(self.url)
        if not all([parsed.scheme, parsed.netloc]):
            raise DomainException("Invalid URL format")
