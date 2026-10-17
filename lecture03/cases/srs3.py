"""СРС 3. Воспроизводимые измерения list и tuple из миллиона элементов."""

import datetime
import json
import platform
import statistics
import sys
import timeit
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict

N = 1_000_000
REPEAT = 7
NUMBER = 5
RESULT_PATH = Path(__file__).resolve().parents[1] / "outputs" / "benchmark.json"


class BenchmarkResult(TypedDict):
    """Типизированные метаданные, повторы и сводка измерения."""

    created_at: str
    python: str
    implementation: str
    platform: str
    n: int
    repeat: int
    number: int
    gc: str
    seconds_per_operation: dict[str, list[float]]
    median_seconds: dict[str, float]
    minimum_seconds: dict[str, float]
    shallow_bytes: dict[str, int]


def iterate(values: Sequence[int]) -> None:
    """Пройти по каждому элементу без вычислений и без вывода на экран."""
    for _ in values:
        pass


def measure() -> BenchmarkResult:
    """Измерить создание, обход и память контейнеров с одинаковыми значениями."""
    list_values = list(range(N))
    tuple_values = tuple(range(N))
    assert len(list_values) == len(tuple_values) == N
    assert list_values[0] == tuple_values[0] == 0
    assert list_values[-1] == tuple_values[-1] == N - 1
    samples = {
        "list_create": timeit.repeat(
            "list(range(N))", globals={"N": N}, repeat=REPEAT, number=NUMBER
        ),
        "tuple_create": timeit.repeat(
            "tuple(range(N))", globals={"N": N}, repeat=REPEAT, number=NUMBER
        ),
        "list_iterate": timeit.repeat(
            "iterate(values)",
            globals={"iterate": iterate, "values": list_values},
            repeat=REPEAT,
            number=NUMBER,
        ),
        "tuple_iterate": timeit.repeat(
            "iterate(values)",
            globals={"iterate": iterate, "values": tuple_values},
            repeat=REPEAT,
            number=NUMBER,
        ),
    }
    seconds = {
        name: [value / NUMBER for value in values] for name, values in samples.items()
    }
    return {
        "created_at": datetime.datetime.now()
        .astimezone()
        .isoformat(timespec="seconds"),
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "n": N,
        "repeat": REPEAT,
        "number": NUMBER,
        "gc": "timeit temporarily disables cyclic garbage collection",
        "seconds_per_operation": seconds,
        "median_seconds": {
            name: statistics.median(values) for name, values in seconds.items()
        },
        "minimum_seconds": {name: min(values) for name, values in seconds.items()},
        "shallow_bytes": {
            "list": sys.getsizeof(list_values),
            "tuple": sys.getsizeof(tuple_values),
        },
    }


def run() -> None:
    """Выполнить реальные измерения и сохранить все повторы в JSON."""
    result = measure()
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Python:", platform.python_version(), platform.python_implementation())
    print("N =", N, "; серий =", REPEAT, "; операций в серии =", NUMBER)
    print("Время одной операции, миллисекунды:")
    for name in ("list_create", "tuple_create", "list_iterate", "tuple_iterate"):
        median = result["median_seconds"][name] * 1000
        minimum = result["minimum_seconds"][name] * 1000
        print(f"{name:14s} медиана {median:9.3f}; минимум {minimum:9.3f}")
    print("sys.getsizeof(list):", result["shallow_bytes"]["list"], "байт")
    print("sys.getsizeof(tuple):", result["shallow_bytes"]["tuple"], "байт")
    print("Память элементов int не входит в sys.getsizeof контейнера.")
    print("Итерация измерена на заранее созданных коллекциях, без print.")
    print("Создание: list(range(N)) и tuple(range(N)); условия одинаковы.")
    print("Все повторы сохранены в lecture03/outputs/benchmark.json.")
