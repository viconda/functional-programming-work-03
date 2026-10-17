"""Дополнение. Вложенные изменяемые объекты и цена конкатенации."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ShallowFrozen:
    """Намеренно небезопасная модель с изменяемым полем."""

    values: list[int]


def run() -> None:
    """Показать поверхностную заморозку и два способа построения кортежа."""
    record = ShallowFrozen([1, 2])
    record.values.append(3)
    print("Список внутри frozen=True изменился:", record.values)
    assert record.values == [1, 2, 3]
    try:
        hash(record)
    except TypeError:
        print("Хеширование записи со списком: TypeError")
    else:
        raise AssertionError("список внутри записи не хешируется")
    nested = ([1], 2)
    nested[0].append(3)
    print("Список внутри tuple тоже изменился:", nested)
    size = 1000
    repeated: tuple[int, ...] = ()
    for value in range(size):
        repeated = repeated + (value,)
    once = tuple(value for value in range(size))
    assert repeated == once and len(once) == size
    print("Оба кортежа равны; длина:", len(once))
    print("Сумма длин новых кортежей при +:", size * (size + 1) // 2)
    print("Разовое построение записывает 1000 ссылок, повторное + имеет O(n²).")
