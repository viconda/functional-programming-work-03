"""Пример 9. Именованный кортеж collections.namedtuple."""

from collections import namedtuple
from typing import Any, cast

Point = namedtuple("Point", ["x", "y"])


def run() -> None:
    """Создать новую версию точки и проверить доступность старой."""
    p = Point(3, 4)
    print(p.x, p.y, p[0])
    q = p._replace(x=10)
    print(p, q)
    print(p._asdict())
    assert p == (3, 4) and q == (10, 4) and p is not q
    try:
        cast(Any, p).x = 5  # Намеренная проверка запрета записи.
    except AttributeError:
        print("Присваивание p.x: AttributeError")
    else:
        raise AssertionError("Point должен быть неизменяемым")
