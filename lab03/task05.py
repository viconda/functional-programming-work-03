"""Задание 5. Сравнение пяти представлений одной записи о книге."""

import gc
import json
import platform
import timeit
import tracemalloc
from collections import namedtuple
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import NamedTuple

BookNamed = namedtuple("BookNamed", "isbn title authors year price")


class BookTyped(NamedTuple):
    """Книга с именами полей и аннотациями типов."""

    isbn: str
    title: str
    authors: tuple[str, ...]
    year: int
    price: int


@dataclass(frozen=True)
class BookFrozen:
    """Замороженная книга; цена задана целым числом тенге."""

    isbn: str
    title: str
    authors: tuple[str, ...]
    year: int
    price: int


def make_factories() -> tuple[tuple[str, Callable[[], object]], ...]:
    """Дать фабрики с общими неизменяемыми значениями полей."""
    isbn, title = "9780132350884", "Чистый код"
    authors, year, price = ("Роберт Мартин",), 2008, 12000
    return (
        (
            "dict",
            lambda: {
                "isbn": isbn,
                "title": title,
                "authors": authors,
                "year": year,
                "price": price,
            },
        ),
        ("tuple", lambda: (isbn, title, authors, year, price)),
        ("namedtuple", lambda: BookNamed(isbn, title, authors, year, price)),
        ("NamedTuple", lambda: BookTyped(isbn, title, authors, year, price)),
        ("frozen dataclass", lambda: BookFrozen(isbn, title, authors, year, price)),
    )


def timed_creation(factory: Callable[[], object], count: int) -> float:
    """Измерить один запуск; освободить записи после остановки таймера."""
    gc.collect()
    holder: list[list[object]] = []
    # holder сохраняет результат, поэтому его удаление не входит в таймер.
    seconds = timeit.timeit(
        lambda: holder.append([factory() for _ in range(count)]), number=1
    )
    assert len(holder[0]) == count
    assert len({id(record) for record in holder[0]}) == count
    return seconds


def measure(factory: Callable[[], object], count: int) -> dict[str, object]:
    """Измерить создание живых записей и отдельно их текущую/пиковую память."""
    if count <= 0:
        raise ValueError("count должен быть положительным")
    times = [timed_creation(factory, count) for _ in range(3)]
    gc.collect()
    tracemalloc.start()
    records = [factory() for _ in range(count)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(records) == count
    return {
        "count": count,
        "seconds": times,
        "best_seconds": min(times),
        "current_bytes": current,
        "peak_bytes": peak,
        "bytes_per_record_including_list": current / count,
    }


def changed_copy(record: object, price: int) -> object:
    """Вернуть запись с новой ценой, сохранив исходную запись."""
    if isinstance(record, dict):
        return {**record, "price": price}
    if isinstance(record, BookFrozen):
        return replace(record, price=price)
    if isinstance(record, BookTyped):
        return record._replace(price=price)
    if isinstance(record, BookNamed):
        return record._replace(price=price)
    if isinstance(record, tuple):
        return record[:4] + (price,)
    raise TypeError("Неизвестное представление книги")


def can_be_key(record: object) -> bool:
    """Проверить именно вставку записи в словарь."""
    try:
        return {record: "книга"}[record] == "книга"
    except TypeError:
        return False


def get_price(record: object) -> int:
    """Прочитать цену из любого из пяти представлений."""
    if isinstance(record, dict):
        return int(record["price"])
    if isinstance(record, BookFrozen):
        return record.price
    if isinstance(record, tuple):
        return int(record[4])
    raise TypeError("Неизвестное представление книги")


def main() -> None:
    """Выполнить измерения, проверки и сохранить реальные результаты JSON."""
    print("ЗАДАНИЕ 5. Создание 100 000 отдельных записей, три повтора")
    print(f"Python {platform.python_version()}, {platform.system()}")
    print("Время без tracemalloc; память отдельно; все поля неизменяемы.")
    results: list[dict[str, object]] = []
    print(f"{'Вид':18} {'min, с':>9} {'живые, MiB':>12} {'пик, MiB':>10} {'ключ':>7}")
    for name, factory in make_factories():
        original = factory()
        updated = changed_copy(original, 15000)
        assert get_price(original) == 12000
        assert get_price(updated) == 15000 and updated is not original
        keyable = can_be_key(original)
        assert keyable == (name != "dict")
        result = {
            "representation": name,
            **measure(factory, 100_000),
            "keyable": keyable,
            "original_price": 12000,
            "updated_price": 15000,
        }
        results.append(result)
        best = float(str(result["best_seconds"]))
        current = int(str(result["current_bytes"])) / 1024**2
        peak = int(str(result["peak_bytes"])) / 1024**2
        print(f"{name:18} {best:9.6f} {current:12.3f} {peak:10.3f} {keyable!s:>7}")
        print(f"  Копия: 12000 -> 15000; исходная цена: {get_price(original)}")
    output = Path(__file__).resolve().parent / "task05_metrics.json"
    payload = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "rows": results,
        "method": "3 repeats, number=1; min; shared immutable payload; "
        "live records retained; tracemalloc run separately",
    }
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Проверки разных объектов, копий и ключей: OK")
    print("Результаты сохранены в lab03/task05_metrics.json")


if __name__ == "__main__":
    main()
