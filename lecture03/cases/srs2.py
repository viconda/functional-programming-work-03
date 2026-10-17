"""СРС 2. Неизменяемая корзина покупок с чистыми операциями."""

from dataclasses import FrozenInstanceError, dataclass, replace
from typing import Any, cast


@dataclass(frozen=True)
class Item:
    """Позиция корзины с ценой в целых тенге и положительным количеством."""

    name: str
    price: int
    quantity: int = 1

    def __post_init__(self) -> None:
        """Проверить допустимость названия, цены и количества."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("название не должно быть пустым")
        if type(self.price) is not int or self.price < 0:
            raise ValueError("цена должна быть целым неотрицательным числом тенге")
        if type(self.quantity) is not int or self.quantity <= 0:
            raise ValueError("количество должно быть целым положительным числом")


@dataclass(frozen=True)
class ShoppingCart:
    """Корзина с уникальными названиями и глубоко неизменяемыми позициями."""

    items: tuple[Item, ...] = ()

    def __post_init__(self) -> None:
        """Не допустить изменяемое поле или дублирующиеся позиции."""
        if type(self.items) is not tuple or any(
            not isinstance(item, Item) for item in self.items
        ):
            raise TypeError("items должен быть кортежем Item")
        if len({item.name for item in self.items}) != len(self.items):
            raise ValueError("названия позиций должны быть уникальными")


def add_item(
    cart: ShoppingCart, name: str, price: int, quantity: int = 1
) -> ShoppingCart:
    """Вернуть корзину с новой позицией либо увеличенным количеством."""
    addition = Item(name, price, quantity)
    found = next((item for item in cart.items if item.name == name), None)
    if found is None:
        return replace(cart, items=cart.items + (addition,))
    if found.price != price:
        raise ValueError("цена существующей позиции должна совпадать")
    return replace(
        cart,
        items=tuple(
            replace(item, quantity=item.quantity + quantity)
            if item.name == name
            else item
            for item in cart.items
        ),
    )


def remove_item(
    cart: ShoppingCart, name: str, quantity: int | None = None
) -> ShoppingCart:
    """Удалить всю позицию при None либо заданное количество; вернуть новую корзину."""
    if quantity is not None and (type(quantity) is not int or quantity <= 0):
        raise ValueError("количество должно быть целым положительным числом")
    found = next((item for item in cart.items if item.name == name), None)
    if found is None:
        raise KeyError(name)
    if quantity is not None and quantity > found.quantity:
        raise ValueError("нельзя удалить больше имеющегося количества")
    if quantity is None or quantity == found.quantity:
        return replace(
            cart, items=tuple(item for item in cart.items if item.name != name)
        )
    return replace(
        cart,
        items=tuple(
            replace(item, quantity=item.quantity - quantity)
            if item.name == name
            else item
            for item in cart.items
        ),
    )


def total(cart: ShoppingCart) -> int:
    """Вычислить стоимость всех позиций в целых тенге."""
    return sum(item.price * item.quantity for item in cart.items)


def run() -> None:
    """Проверить добавление, удаление, сохранение версий и неверные операции."""
    c0 = ShoppingCart()
    c1 = add_item(c0, "Книга", 3500, 2)
    c2 = add_item(c1, "Ручка", 250, 3)
    c3 = add_item(c2, "Книга", 3500)
    c4 = remove_item(c3, "Книга", 1)
    c5 = remove_item(c4, "Ручка")
    for index, cart in enumerate((c0, c1, c2, c3, c4, c5)):
        print(
            f"c{index}:",
            [(i.name, i.quantity) for i in cart.items],
            "итог:",
            total(cart),
            "тг",
        )
    assert c0.items == () and c1.items[0].quantity == 2
    assert [total(c) for c in (c0, c1, c2, c3, c4, c5)] == [
        0,
        7000,
        7750,
        11250,
        7750,
        7000,
    ]
    assert c2.items[1] is c3.items[1]
    assert remove_item(c5, "Книга", 2) == c0
    assert add_item(c0, "Книга", 3500, 2) == c1
    invalid = [
        lambda: add_item(c1, "Книга", 3600),
        lambda: add_item(c0, "", 10),
        lambda: add_item(c0, "X", -1),
        lambda: add_item(c0, "X", 1, 0),
        lambda: remove_item(c1, "Нет"),
        lambda: remove_item(c1, "Книга", 3),
        lambda: remove_item(c1, "Книга", 0),
    ]
    for operation in invalid:
        try:
            operation()
        except (ValueError, KeyError):
            pass
        else:
            raise AssertionError("неверная операция должна быть отклонена")
    try:
        cast(Any, c1).items = ()  # Намеренная проверка заморозки.
    except FrozenInstanceError:
        print("Присваивание полю: FrozenInstanceError")
    else:
        raise AssertionError("корзина должна быть неизменяемой")
    assert hash(c1) == hash(add_item(c0, "Книга", 3500, 2))
    print(
        "Старые версии сохранены; общая неизменённая позиция:",
        c2.items[1] is c3.items[1],
    )
    print("Проверено 7 ошибочных операций; все отклонены.")
