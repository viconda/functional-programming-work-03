"""Задание 3. Две записи одного конвейера без циклов в алгоритме."""

from collections.abc import Sequence
from operator import itemgetter
from typing import TypeAlias

Product: TypeAlias = tuple[str, str, int, float]
Result: TypeAlias = tuple[Product | None, list[Product], Product | None]


def solve_lambda(products: Sequence[Product]) -> Result:
    """Найти лучший товар, технику по цене и самый дешёвый товар с рейтингом 4.5+."""
    best = max(products, key=lambda product: product[3], default=None)
    tech = sorted(
        filter(lambda product: product[1] == "техника", products),
        key=lambda product: product[2],
    )
    cheapest_good = min(
        filter(lambda product: product[3] >= 4.5, products),
        key=lambda product: product[2],
        default=None,
    )
    return best, tech, cheapest_good


def solve_itemgetter(products: Sequence[Product]) -> Result:
    """Выполнить тот же конвейер, используя itemgetter для доступа к полям."""
    best = max(products, key=itemgetter(3), default=None)
    tech = sorted(
        filter(lambda product: itemgetter(1)(product) == "техника", products),
        key=itemgetter(2),
    )
    cheapest_good = min(
        filter(lambda product: itemgetter(3)(product) >= 4.5, products),
        key=itemgetter(2),
        default=None,
    )
    return best, tech, cheapest_good


def main() -> None:
    """Сравнить результаты двух реализаций и проверить крайние случаи."""
    products: list[Product] = [
        ("Ноутбук", "техника", 450000, 4.7),
        ("Чайник", "быт", 15000, 4.2),
        ("Смартфон", "техника", 320000, 4.9),
        ("Утюг", "быт", 22000, 3.9),
        ("Наушники", "техника", 45000, 4.5),
    ]
    original = products.copy()
    lambda_result = solve_lambda(products)
    getter_result = solve_itemgetter(products)
    expected: Result = (
        products[2],
        [products[4], products[2], products[0]],
        products[4],
    )
    assert lambda_result == getter_result == expected
    assert products == original and lambda_result[1] is not products
    assert solve_lambda([]) == solve_itemgetter([]) == (None, [], None)
    only_bad: list[Product] = [("Утюг", "быт", 22000, 3.9)]
    assert (
        solve_lambda(only_bad) == solve_itemgetter(only_bad) == (only_bad[0], [], None)
    )
    ties: list[Product] = [("A", "техника", 10, 4.5), ("B", "техника", 10, 4.5)]
    assert solve_lambda(ties) == solve_itemgetter(ties) == (ties[0], ties, ties[0])
    print("ЗАДАНИЕ 3. sorted, max, min, filter и lambda")
    print("Вариант с lambda:")
    print("  Лучший товар:", lambda_result[0])
    print("  Техника по возрастанию цены:")
    print(" ", lambda_result[1][0])
    print(" ", lambda_result[1][1])
    print(" ", lambda_result[1][2])
    print("  Дешёвый с рейтингом >= 4.5:", lambda_result[2])
    print("Вариант с itemgetter:")
    print("  Лучший товар:", getter_result[0])
    print("  Техника по возрастанию цены:")
    print(" ", getter_result[1][0])
    print(" ", getter_result[1][1])
    print(" ", getter_result[1][2])
    print("  Дешёвый с рейтингом >= 4.5:", getter_result[2])
    print("Варианты совпадают:", lambda_result == getter_result)
    print("Исходный список сохранён:", products == original)
    print("Пустой список:", solve_lambda([]))
    print("Нет подходящего товара:", solve_lambda(only_bad))
    print("При равенстве ключей сохраняется первый товар:", solve_lambda(ties)[0])
    print("itemgetter короче для ключей; lambda яснее выражает условие отбора.")
    print("ПРОВЕРКИ: исходные данные, оба алгоритма и граничные случаи пройдены.")


if __name__ == "__main__":
    main()
