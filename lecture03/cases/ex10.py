"""Пример 10. Типизированная запись с методами."""

import math
from typing import NamedTuple


class Vector(NamedTuple):
    """Двумерный вектор, представленный неизменяемой записью."""

    x: float
    y: float = 0.0

    def length(self) -> float:
        """Вернуть евклидову длину вектора."""
        return math.hypot(self.x, self.y)

    def scaled(self, k: float) -> "Vector":
        """Вернуть новый вектор, умноженный на коэффициент k."""
        return Vector(self.x * k, self.y * k)


def run() -> None:
    """Проверить методы, значение по умолчанию и отсутствие мутации."""
    v = Vector(3, 4)
    print(v.length(), v.scaled(2), Vector(5))
    assert v.length() == 5.0 and v.scaled(2) == Vector(6, 8)
    assert v == Vector(3, 4) and Vector(5).y == 0.0
    assert v.scaled(0) == Vector(0, 0)
