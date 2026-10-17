"""Пример 15. Лямбда-выражения для фильтрации и сортировки товаров."""

from typing import NamedTuple


class Product(NamedTuple):
    """Товар с ценой и количеством на складе."""

    name: str
    price: int
    qty: int


def run() -> None:
    """Отобрать товары в наличии и упорядочить по стоимости запаса."""
    stock = (
        Product("Ноутбук", 450_000, 3),
        Product("Мышь", 7_000, 40),
        Product("Монитор", 120_000, 0),
    )
    in_stock = tuple(filter(lambda p: p.qty > 0, stock))
    by_value = sorted(stock, key=lambda p: p.price * p.qty, reverse=True)
    print([p.name for p in in_stock])
    print([p.name for p in by_value])
    print("Стоимость запаса:", [p.price * p.qty for p in by_value])
    assert [p.name for p in in_stock] == ["Ноутбук", "Мышь"]
    assert [p.name for p in by_value] == ["Ноутбук", "Мышь", "Монитор"]
    assert len(stock) == 3
