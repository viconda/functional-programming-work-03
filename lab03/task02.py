"""Задание 2. Ошибочные defaults из условия и чистые исправления."""

from collections.abc import Mapping
from datetime import datetime
from time import sleep
from types import FunctionType
from typing import TypedDict, cast


class Registration(TypedDict):
    """Регистрация с неизменяемым набором ролей."""

    name: str
    roles: frozenset[str]


class Record(TypedDict):
    """Текстовая запись с явно заданным временем."""

    text: str
    created: datetime


def log_event(event: str, journal: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Вернуть новый журнал с событием, сохранив предыдущую версию."""
    return journal + (event,)


def register(name: str, roles: frozenset[str] = frozenset()) -> Registration:
    """Создать регистрацию, сохранив исходные роли и добавив student."""
    return {"name": name, "roles": roles | {"student"}}


def cache_square(
    n: int,
    cache: Mapping[int, int] | None = None,
) -> tuple[int, dict[int, int]]:
    """Вернуть квадрат и новый кэш без изменения переданного состояния."""
    previous = {} if cache is None else cache
    if n in previous:
        return previous[n], dict(previous)
    result = n * n
    return result, {**previous, n: result}


def make_record(text: str, *, created: datetime) -> Record:
    """Создать запись с явным временем, одинаковым для одинаковых аргументов."""
    return {"text": text, "created": created}


def make_record_now(text: str) -> Record:
    """Получить часы системы на границе ввода-вывода и вызвать чистое ядро."""
    return make_record(text, created=datetime.now())


def main() -> None:
    """Продемонстрировать четыре исходные ошибки и проверить исправления."""

    # Только учебная демонстрация. Эти функции намеренно повторяют ошибки условия.
    # Они определяются локально и не входят в рабочий API модуля.
    def bad_log_event(event: str, journal: list[str] = []) -> list[str]:  # noqa: B006
        journal.append(event)
        return journal

    def bad_register(
        name: str,
        roles: set[str] = set(),  # noqa: B006
    ) -> dict[str, object]:
        roles.add("student")
        return {"name": name, "roles": roles}

    def bad_cache_square(n: int, cache: dict[int, int] = {}) -> int:  # noqa: B006
        if n not in cache:
            cache[n] = n * n
        return cache[n]

    def bad_make_record(
        text: str,
        created: datetime = datetime.now(),  # noqa: B008
    ) -> Record:
        return {"text": text, "created": created}

    print("ЗАДАНИЕ 2. Изменяемые и устаревающие defaults")
    first_log = bad_log_event("вход")
    second_log = bad_log_event("выход")
    assert first_log is second_log and first_log == ["вход", "выход"]
    print("1. До: первый журнал после второго вызова =", first_log)
    print("   Оба вызова вернули один список:", first_log is second_log)
    old_log = ("вход",)
    new_log = log_event("выход", old_log)
    assert old_log == ("вход",) and new_log == ("вход", "выход")
    assert log_event("A") == ("A",) and log_event("B") == ("B",)
    print("   После: старый журнал =", old_log, "; новый =", new_log)

    first_person = bad_register("Алия")
    second_person = bad_register("Аскар")
    shared_roles = first_person["roles"]
    assert isinstance(shared_roles, set)
    shared_roles.add("admin")
    assert first_person["roles"] is second_person["roles"]
    print(
        "2. До: добавление admin первому изменило роли второго:", sorted(shared_roles)
    )
    initial_roles = frozenset({"reader"})
    fixed_person = register("Алия", initial_roles)
    independent = register("Аскар")
    assert initial_roles == frozenset({"reader"})
    assert fixed_person["roles"] == frozenset({"reader", "student"})
    assert independent["roles"] == frozenset({"student"})
    print(
        "   После: Алия =",
        sorted(fixed_person["roles"]),
        "; Аскар =",
        sorted(independent["roles"]),
    )

    assert bad_cache_square(4) == 16
    bad_defaults = cast(FunctionType, bad_cache_square).__defaults__
    assert bad_defaults is not None
    assert bad_defaults[0] == {4: 16}
    print("3. До: кэш после вызова cache_square(4) =", bad_defaults[0])
    bad_defaults[0][4] = 999
    assert bad_cache_square(4) == 999
    print(
        "   Изменение скрытого состояния меняет результат: cache_square(4) =",
        bad_cache_square(4),
    )
    empty_cache: dict[int, int] = {}
    result, cache_v1 = cache_square(4, empty_cache)
    result_again, cache_v2 = cache_square(4, cache_v1)
    assert result == result_again == 16 and empty_cache == {}
    assert cache_v1 == cache_v2 == {4: 16} and cache_v1 is not cache_v2
    assert cache_square(-3) == (9, {-3: 9}) and cache_square(0) == (0, {0: 0})
    print(
        "   После: результат =",
        result,
        "; исходный кэш =",
        empty_cache,
        "; новый =",
        cache_v1,
    )

    record_a = bad_make_record("A")
    sleep(0.01)  # Пауза только в демонстрации: часы идут, default остаётся прежним.
    record_b = bad_make_record("B")
    assert record_a["created"] is record_b["created"]
    print(
        "4. До: время обоих вызовов =",
        record_a["created"].isoformat(timespec="microseconds"),
    )
    print(
        "   Это один объект, сохранённый при def:",
        record_a["created"] is record_b["created"],
    )
    fixed_time = datetime(2026, 10, 17, 12, 0, 0)
    pure_record = make_record("A", created=fixed_time)
    assert pure_record == make_record("A", created=fixed_time)
    assert pure_record is not make_record("A", created=fixed_time)
    print("   После: чистая запись =", pure_record)
    current_record = make_record_now("граница ввода-вывода")
    assert isinstance(current_record["created"], datetime)
    print(
        "   make_record_now читает реальные часы:",
        current_record["created"].isoformat(timespec="microseconds"),
    )
    print("Общий кэш может быть намеренным, но скрытое изменяемое состояние нечисто.")
    print("Чтение datetime.now тоже нечисто; время передаётся в чистое ядро явно.")
    print("ПРОВЕРКИ: четыре исходные ошибки воспроизведены, исправления пройдены.")


if __name__ == "__main__":
    main()
