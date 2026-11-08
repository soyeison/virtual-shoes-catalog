from typing import List
from dataclasses import dataclass, field
from app.domain.value_objects.image_url import ImageURL
from app.domain.value_objects.stock import Stock
from app.domain.value_objects.price import Price
from app.domain.exceptions import DomainException


@dataclass
class Article:
    id: str
    name: str
    description: str
    price: Price
    stock: Stock
    image_urls: List[ImageURL] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        id: str,
        name: str,
        description: str,
        initial_stock: Stock,
        initial_price: Price,
    ) -> "Article":
        if not name.strip():
            raise DomainException("Article name cannot be empty")

        return cls(
            id=id,
            name=name,
            description=description,
            stock=initial_stock,
            price=initial_price,
        )

    # -------------- Setters for updating user information --------------
    def update_name(self, new_name: str):
        if not new_name.strip():
            raise DomainException("Article name cannot be empty")
        self.name = new_name

    def update_description(self, new_description: str):
        self.description = new_description

    def update_price(self, new_price: Price):
        self.price = new_price

    # -------------- Getters for retrieving user information ------------
    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description

    def get_price(self) -> Price:
        return self.price

    def get_stock(self) -> Stock:
        return self.stock

    def get_image_urls(self) -> List[ImageURL]:
        return list(self.image_urls)

    # ----------------------- Bussiness Logic ---------------------------

    def attach_image(self, image_url: ImageURL):
        if len(self.image_urls) >= 5:
            raise DomainException("Cannot attach more than 5 images to an article")

        self.image_urls.append(image_url)

    def sell_item(self, quantity: int):
        self.stock = self.stock.decrease(quantity)

    def restock_item(self, quantity: int):
        self.stock = self.stock.add(quantity)

    def decrease_stock(self, quantity: int) -> None:
        self.stock = self.stock.decrease(quantity)
