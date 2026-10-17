"""Пример 6. Интроспекция функции без отложенного вычисления аннотаций."""

import inspect


def scale(x: float, factor: float = 2.0, *, clip: bool = False) -> float:
    """Масштабировать значение."""
    y = x * factor
    return min(y, 1.0) if clip else y


def run() -> None:
    """Прочитать атрибуты, сигнатуру и проверить флаг ограничения."""
    print(scale.__defaults__, scale.__kwdefaults__)
    print(scale.__annotations__)
    print(inspect.signature(scale))
    print("Имя:", scale.__name__, "Документация:", scale.__doc__)
    print("Аргументы:", scale.__code__.co_varnames[:3], "Замыкание:", scale.__closure__)
    assert scale(0.75) == 1.5 and scale(0.75, clip=True) == 1.0
    assert scale(-2, clip=True) == -4.0
    assert scale.__defaults__ == (2.0,)
    assert scale.__kwdefaults__ == {"clip": False}
