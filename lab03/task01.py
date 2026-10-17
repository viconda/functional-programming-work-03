"""Задание 1. Сигнатуры, корректные вызовы и ошибки связывания аргументов."""

import inspect
import math
from collections.abc import Callable, Mapping, Sequence
from statistics import mean, median
from textwrap import fill
from types import FunctionType
from typing import Any, TypedDict, cast


class PriceOptions(TypedDict):
    """Тип двух именованных аргументов для примера распаковки словаря."""

    discount: float
    tax: float


def stats(*numbers: float, precision: int = 2) -> dict[str, float]:
    """Вернуть минимум, максимум, среднее и медиану непустого набора чисел."""
    if not numbers:
        raise ValueError("Нужен хотя бы один элемент")
    if not isinstance(precision, int) or isinstance(precision, bool):
        raise TypeError("precision должен быть целым числом")
    if not all(math.isfinite(number) for number in numbers):
        raise ValueError("Все числа должны быть конечными")
    return {
        "min": round(float(min(numbers)), precision),
        "max": round(float(max(numbers)), precision),
        "mean": round(float(mean(numbers)), precision),
        "median": round(float(median(numbers)), precision),
    }


def make_table(
    title: str,
    /,
    *rows: Sequence[object],
    sep: str = " | ",
    header: Sequence[object] | None = None,
) -> str:
    """Сформировать текстовую таблицу, не меняя строки и заголовок."""
    all_rows = (header,) + rows if header is not None else rows
    return "\n".join((title, *(sep.join(map(str, row)) for row in all_rows)))


def price(
    amount: float,
    /,
    *,
    currency: str = "KZT",
    discount: float = 0.0,
    tax: float = 0.12,
) -> str:
    """Вернуть цену с валютой: сначала скидка, затем налог, округление до тиынов."""
    if not all(math.isfinite(value) for value in (amount, discount, tax)):
        raise ValueError("Цена, скидка и налог должны быть конечными")
    if amount < 0 or not 0 <= discount <= 1 or tax < 0:
        raise ValueError("Нужны amount >= 0, discount от 0 до 1, tax >= 0")
    if not currency.strip():
        raise ValueError("Валюта не должна быть пустой")
    return f"{amount * (1 - discount) * (1 + tax):.2f} {currency}"


def merge_settings(
    defaults: Mapping[str, object],
    /,
    **overrides: object,
) -> dict[str, object]:
    """Вернуть новый словарь; запретить неизвестные имена настроек."""
    unknown = overrides.keys() - defaults.keys()
    if unknown:
        raise KeyError(f"Неизвестные настройки: {', '.join(sorted(unknown))}")
    return {**defaults, **overrides}


def main() -> None:
    """Выполнить проверки и вывести доказательства допустимых способов вызова."""
    functions: tuple[Callable[..., object], ...] = (
        stats,
        make_table,
        price,
        merge_settings,
    )
    print("ЗАДАНИЕ 1. Сигнатуры функций")
    for function in functions:
        print(fill(f"{function.__name__}{inspect.signature(function)}", width=90))
        attributes = cast(FunctionType, function)
        print("  __defaults__ =", attributes.__defaults__)
        print("  __kwdefaults__ =", attributes.__kwdefaults__)

    values = (1.25, 2.5, 3.75, 8.0)
    expected = {"min": 1.25, "max": 8.0, "mean": 3.88, "median": 3.12}
    assert stats(*values) == expected
    assert stats(5) == {"min": 5.0, "max": 5.0, "mean": 5.0, "median": 5.0}
    assert stats(120, 180, precision=-2)["mean"] == 200.0
    precision_options = {"precision": 0}
    assert stats(1, 2, precision=0) == stats(*(1, 2), **precision_options)
    print("stats(1.25, 2.5, 3.75, 8.0) =", stats(*values))
    print("stats(*values, precision=1) =", stats(*values, precision=1))
    print("stats(5) =", stats(5))
    rows = (("Алия", 95), ("Аскар", 87))
    header = ("Имя", "Балл")
    assert make_table("Оценки", *rows, header=header) == (
        "Оценки\nИмя | Балл\nАлия | 95\nАскар | 87"
    )
    assert make_table("Пустая таблица") == "Пустая таблица"
    assert make_table("Числа", (1, 2), sep=",") == "Числа\n1,2"
    table_options = {"sep": ";"}
    assert make_table("X", (1, 2), **table_options) == "X\n1;2"
    print("make_table('Оценки', *rows, header=header):")
    print(make_table("Оценки", *rows, header=header))
    print(
        "make_table('Числа', (1, 2), sep=',') =",
        repr(make_table("Числа", (1, 2), sep=",")),
    )
    assert price(1000) == "1120.00 KZT"
    assert price(1000, currency="USD", discount=0.1, tax=0) == "900.00 USD"
    assert price(1000, discount=0.1) == "1008.00 KZT"
    assert price(0) == "0.00 KZT"
    assert price(1000, discount=1) == "0.00 KZT"
    price_options: PriceOptions = {"discount": 0.1, "tax": 0.12}
    assert price(1000, **price_options) == "1008.00 KZT"
    print("price(1000) =", price(1000))
    print("price(1000, discount=0.1) =", price(1000, discount=0.1))
    print(
        "price(1000, currency='USD', tax=0, discount=0.1) =",
        price(1000, currency="USD", tax=0, discount=0.1),
    )
    defaults: dict[str, object] = {"theme": "light", "size": 12}
    changed = merge_settings(defaults, theme="dark")
    assert changed == {"theme": "dark", "size": 12}
    assert changed is not defaults and defaults == {"theme": "light", "size": 12}
    assert merge_settings(defaults) == defaults
    assert merge_settings(defaults) is not defaults
    setting_options = {"size": 14}
    assert merge_settings(defaults, **setting_options)["size"] == 14
    print("merge_settings(defaults, theme='dark') =", changed)
    print("Исходные настройки =", defaults)
    assert rows == (("Алия", 95), ("Аскар", 87)) and header == ("Имя", "Балл")

    # Динамический тип нужен только для намеренно неверных демонстрационных вызовов.
    dynamic_stats = cast(Callable[..., Any], stats)
    dynamic_table = cast(Callable[..., Any], make_table)
    dynamic_price = cast(Callable[..., Any], price)
    dynamic_merge = cast(Callable[..., Any], merge_settings)
    repeated_precision = {"precision": 3}
    wrong_calls: tuple[tuple[str, Callable[[], object]], ...] = (
        (
            "stats(numbers=(1, 2)): *numbers не именованный параметр",
            lambda: dynamic_stats(numbers=(1, 2)),
        ),
        (
            "stats(1, precision=2, **{'precision': 3}): повтор имени",
            lambda: dynamic_stats(1, precision=2, **repeated_precision),
        ),
        (
            "make_table(title='X'): title только по позиции",
            lambda: dynamic_table(title="X"),
        ),
        ("make_table(): обязательный title отсутствует", lambda: dynamic_table()),
        (
            "price(amount=1000): amount только по позиции",
            lambda: dynamic_price(amount=1000),
        ),
        (
            "price(1000, 'USD'): currency только по имени",
            lambda: dynamic_price(1000, "USD"),
        ),
        (
            "price(1000, unknown=1): нет **kwargs",
            lambda: dynamic_price(1000, unknown=1),
        ),
        (
            "merge_settings(defaults={}): defaults не передан по позиции",
            lambda: dynamic_merge(defaults={}),
        ),
        (
            "merge_settings({}, {}): второй позиционный аргумент запрещён",
            lambda: dynamic_merge({}, {}),
        ),
    )
    print("\nНамеренно неверные вызовы:")
    for explanation, call in wrong_calls:
        try:
            call()
        except TypeError:
            print("TypeError:", explanation)
        else:
            raise AssertionError("Ожидалась ошибка TypeError")
    try:
        merge_settings(defaults, unknown=True)
    except KeyError as error:
        print("KeyError:", error)
    else:
        raise AssertionError("Неизвестная настройка должна быть отклонена")
    for call in (lambda: stats(), lambda: price(-1), lambda: price(1, discount=1.1)):
        try:
            call()
        except ValueError:
            pass
        else:
            raise AssertionError("Ожидалась проверка границ")
    print("ПРОВЕРКИ: допустимые вызовы, ошибки, границы и неизменность пройдены.")


if __name__ == "__main__":
    main()
