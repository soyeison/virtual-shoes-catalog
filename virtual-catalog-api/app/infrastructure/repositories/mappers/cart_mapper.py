import json
import sqlite3
from typing import Dict, Any
from app.domain.aggregates.cart import Cart
from app.domain.value_objects.cart_item import CartItem


class CartMapper:
    @staticmethod
    def to_domain(row: sqlite3.Row | Dict[str, Any]) -> Cart:
        cart = Cart.initialize(user_id=row["user_id"])

        items_data = json.loads(row["items"]) if row["items"] else []

        items_dict = {
            item["article_id"]: CartItem(
                article_id=item["article_id"], quantity=item["quantity"]
            )
            for item in items_data
        }

        return Cart.reconstitute(user_id=row["user_id"], items=items_dict)

    @staticmethod
    def to_persistence(cart: Cart) -> tuple:
        items_list = [
            {"article_id": item.article_id, "quantity": item.quantity}
            for item in cart.get_items()
        ]

        items_json = json.dumps(items_list)

        return (cart.user_id, items_json)
