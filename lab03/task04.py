"""Задание 4. frozenset, MappingProxyType, Enum и рекурсивная заморозка."""

from collections.abc import Mapping, MutableMapping
from copy import deepcopy
from enum import Enum
from types import MappingProxyType
from typing import cast


class Weekday(Enum):
    """Дни недели с явно заданными постоянными значениями."""

    MONDAY = "Понедельник"
    TUESDAY = "Вторник"
    WEDNESDAY = "Среда"
    THURSDAY = "Четверг"
    FRIDAY = "Пятница"
    SATURDAY = "Суббота"
    SUNDAY = "Воскресенье"


def is_weekend(day: Weekday) -> bool:
    """Проверить, относится ли день к субботе или воскресенью."""
    return day in (Weekday.SATURDAY, Weekday.SUNDAY)


def with_option(
    config: Mapping[str, object],
    key: str,
    value: object,
) -> Mapping[str, object]:
    """Создать новое представление отдельного словаря с заменённой опцией."""
    return MappingProxyType({**config, key: value})


def freeze(obj: object) -> object:
    """Рекурсивно заморозить ациклические встроенные контейнеры и скаляры.

    Списки и кортежи обходятся рекурсивно. Словарь копируется в новый
    MappingProxyType. Его наличие исключает гарантию хешируемости.
    Произвольные пользовательские объекты отклоняются, так как их
    внутреннюю изменяемость невозможно определить по общему интерфейсу.
    """
    if isinstance(obj, Mapping):
        return MappingProxyType(
            {freeze(key): freeze(value) for key, value in obj.items()}
        )
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(item) for item in obj)
    if isinstance(obj, (set, frozenset)):
        return frozenset(freeze(item) for item in obj)
    if obj is None or isinstance(obj, (bool, int, float, complex, str, bytes, Enum)):
        return obj
    raise TypeError(f"Тип {type(obj).__name__} не поддерживается функцией freeze")


def main() -> None:
    """Проверить операции с коллекциями, запрет записи и хешируемость."""
    print("ЗАДАНИЕ 4. Неизменяемые коллекции")
    candidate_a = frozenset({"Python", "SQL", "Git", "Docker"})
    candidate_b = frozenset({"Python", "Git", "Java"})
    candidate_c = frozenset({"Python", "Git", "SQL", "Linux"})
    common = candidate_a & candidate_b & candidate_c
    first_only = candidate_a - (candidate_b | candidate_c)
    all_skills = candidate_a | candidate_b | candidate_c
    positions = {candidate_a: "Backend-разработчик", candidate_b: "Java-разработчик"}
    assert common == frozenset({"Python", "Git"})
    assert first_only == frozenset({"Docker"})
    assert all_skills == frozenset({"Python", "SQL", "Git", "Docker", "Java", "Linux"})
    assert (
        positions[frozenset({"Git", "Docker", "SQL", "Python"})]
        == "Backend-разработчик"
    )
    assert candidate_a == frozenset({"Python", "SQL", "Git", "Docker"})
    print("Кандидат 1:", sorted(candidate_a))
    print("Кандидат 2:", sorted(candidate_b))
    print("Кандидат 3:", sorted(candidate_c))
    print("Общие навыки:", sorted(common))
    print("Только у первого:", sorted(first_only))
    print("Все навыки:", sorted(all_skills))
    print("Должность по ключу frozenset:", positions[candidate_a])

    config: Mapping[str, object] = MappingProxyType({"theme": "light", "port": 8080})
    try:
        cast(MutableMapping[str, object], config)["port"] = 9000
    except TypeError:
        print("Прямое изменение MappingProxyType: TypeError")
    else:
        raise AssertionError("MappingProxyType должен запретить запись")
    new_config = with_option(config, "port", 9000)
    extended = with_option(config, "debug", True)
    assert dict(config) == {"theme": "light", "port": 8080}
    assert new_config["port"] == 9000 and "debug" not in config
    assert extended["debug"] is True and new_config is not config
    print("Исходная конфигурация:", dict(config))
    print("Новая конфигурация:", dict(new_config))
    backing: dict[str, object] = {"port": 8080}
    live_proxy = MappingProxyType(backing)
    independent = with_option(live_proxy, "theme", "dark")
    backing["port"] = 7070
    assert live_proxy["port"] == 7070 and independent["port"] == 8080
    print("Внешнее изменение backing видно в proxy:", live_proxy["port"])
    print("Новая конфигурация имеет свой словарь:", independent["port"])

    weekdays = [day.value for day in Weekday if not is_weekend(day)]
    assert len(weekdays) == 5 and is_weekend(Weekday.SATURDAY)
    assert is_weekend(Weekday.SUNDAY) and not is_weekend(Weekday.MONDAY)
    print("Рабочие дни:", ", ".join(weekdays))

    source = [1, [2, 3], {4, 5}, ("x", [6])]
    before = deepcopy(source)
    frozen = freeze(source)
    assert frozen == (1, (2, 3), frozenset({4, 5}), ("x", (6,)))
    assert source == before and freeze(frozen) == frozen
    hash(frozen)
    frozen_keys: dict[object, str] = {frozen: "корректный ключ"}
    assert frozen_keys[freeze(source)] == "корректный ключ"
    print("freeze вложенной структуры:", frozen)
    print("Без вложенных MappingProxyType hash() выполнен успешно.")
    nested = {"items": [1, {"skills": {"Python", "Git"}}]}
    frozen_nested = freeze(nested)
    assert isinstance(frozen_nested, Mapping)
    items = frozen_nested["items"]
    assert isinstance(items, tuple) and isinstance(items[1], Mapping)
    assert items[1]["skills"] == frozenset({"Python", "Git"})
    nested["items"].append(2)
    assert len(items) == 2
    for unhashable in (frozen_nested, (frozen_nested,)):
        try:
            hash(unhashable)
        except TypeError:
            pass
        else:
            raise AssertionError(
                "MappingProxyType или содержащий его кортеж не хешируется"
            )
    assert freeze(frozenset({(1, 2), (3, 4)})) == frozenset({(1, 2), (3, 4)})
    print("Словарь скопирован; изменение исходного списка не меняет заморозку.")
    print("MappingProxyType и кортеж с ним: ожидаемый TypeError при hash().")
    print(
        "ПРОВЕРКИ: множества, конфигурация, дни, рекурсия и исходные данные пройдены."
    )


if __name__ == "__main__":
    main()
