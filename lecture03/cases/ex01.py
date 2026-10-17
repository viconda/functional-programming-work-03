"""Пример 1. Определение функции, return и свойства объекта-функции."""


def hypotenuse(a: float, b: float) -> float:
    """Вернуть длину гипотенузы прямоугольного треугольника с катетами a и b."""
    return (a**2 + b**2) ** 0.5


def run() -> None:
    """Выполнить исходный пример и проверить результат."""
    print(hypotenuse(3, 4))
    print(hypotenuse.__name__, "|", hypotenuse.__doc__)
    assert hypotenuse(3, 4) == 5.0
    assert hypotenuse(0, 0) == 0.0
    assert hypotenuse(5, 12) == 13.0
    assert run.__annotations__["return"] is None
