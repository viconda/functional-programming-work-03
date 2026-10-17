"""Пример 7. Операции над кортежем, память и условная хешируемость."""

import sys
from typing import Any, cast


def run() -> None:
    """Выполнить операции лекции и проверить неизменяемость кортежа."""
    t = (1, 2, 3)
    lst = [1, 2, 3]
    print(sys.getsizeof(t) < sys.getsizeof(lst))
    print(t + (4,), t * 2, t[::-1])
    print(hash(t) == hash((1, 2, 3)))
    print("Размеры tuple/list:", sys.getsizeof(t), sys.getsizeof(lst), "байт")
    assert t == (1, 2, 3) and t.count(2) == 1 and t.index(3) == 2
    try:
        cast(Any, t)[0] = 9  # Намеренная проверка запрета записи.
    except TypeError:
        print("Изменение элемента: TypeError")
    else:
        raise AssertionError("кортеж оказался изменяемым")
    try:
        hash(([1], 2))
    except TypeError:
        print("Кортеж со списком не хешируется: TypeError")
    else:
        raise AssertionError("список не должен быть хешируемым")
