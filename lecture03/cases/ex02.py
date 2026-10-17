"""Пример 2. Возвращение нескольких статистик и распаковка кортежа."""

from collections.abc import Sequence


def min_max_mean(values: Sequence[float]) -> tuple[float, float, float]:
    """Вернуть минимум, максимум и среднее непустой последовательности."""
    if not values:
        raise ValueError("последовательность не должна быть пустой")
    n = len(values)
    return min(values), max(values), sum(values) / n


def run() -> None:
    """Проверить статистики, отсутствие мутации и обработку пустого ввода."""
    values = [4, 8, 15, 16, 23, 42]
    before = values.copy()
    lo, hi, avg = min_max_mean(values)
    print(lo, hi, avg)
    assert (lo, hi, avg) == (4, 42, 18.0)
    assert values == before
    assert min_max_mean([7]) == (7, 7, 7.0)
    try:
        min_max_mean([])
    except ValueError as exc:
        print("Пустой ввод:", str(exc))
    else:
        raise AssertionError("ожидался ValueError")
