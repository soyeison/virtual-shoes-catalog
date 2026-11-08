from dataclasses import dataclass
from typing import Optional


@dataclass
class ArticleCriteria:
    name_contains: str | None = None

    min_price: Optional[float] = None
    max_price: Optional[float] = None

    sort_by: Optional[str] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0
