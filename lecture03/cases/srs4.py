"""СРС 4. Рекурсивное преобразование вложенных коллекций."""

from types import MappingProxyType
from typing import Any, cast


def freeze(obj: Any) -> Any:
    """Заморозить ациклические коллекции; сохранить неизменяемые скаляры.

    Поддерживаются list, tuple, set, frozenset, dict, MappingProxyType и
    скаляры None, bool, int, float, complex, str, bytes. Циклы отклоняются,
    так как обычный tuple не может непосредственно содержать самого себя.
    Неподдерживаемые пользовательские объекты отклоняются явно.
    """
    active: set[int] = set()
    memo: dict[int, Any] = {}

    def convert(value: Any) -> Any:
        """Преобразовать одну ветвь, обнаруживая циклы и сохраняя общие подветви."""
        if value is None or type(value) in (bool, int, float, complex, str, bytes):
            return value
        if type(value) not in (list, tuple, set, frozenset, dict, MappingProxyType):
            raise TypeError(f"неподдерживаемый тип: {type(value).__name__}")
        identity = id(value)
        if identity in active:
            raise ValueError(
                "циклическую структуру нельзя преобразовать "
                "в обычные неизменяемые контейнеры"
            )
        if identity in memo:
            return memo[identity]
        active.add(identity)
        result: Any
        try:
            if isinstance(value, (list, tuple)):
                result = tuple(convert(item) for item in value)
            elif isinstance(value, (set, frozenset)):
                result = frozenset(convert(item) for item in value)
            else:
                result = MappingProxyType(
                    {convert(key): convert(item) for key, item in value.items()}
                )
            memo[identity] = result
            return result
        finally:
            active.remove(identity)

    return convert(obj)


def run() -> None:
    """Проверить все преобразования, независимость от оригинала и границы."""
    source: dict[str, Any] = {
        "students": [{"name": "Алия", "scores": [80, 90]}],
        "tags": {"fp", "python"},
    }
    result = freeze(source)
    print("Внешний тип:", type(result).__name__)
    print("students:", type(result["students"]).__name__)
    print("Запись студента:", type(result["students"][0]).__name__)
    print("scores:", result["students"][0]["scores"])
    print("tags:", type(result["tags"]).__name__, sorted(result["tags"]))
    assert isinstance(result, MappingProxyType)
    assert isinstance(result["students"], tuple)
    assert isinstance(result["students"][0], MappingProxyType)
    assert result["students"][0]["scores"] == (80, 90)
    assert result["tags"] == frozenset({"fp", "python"})
    source["students"][0]["scores"].append(100)
    source["tags"].add("new")
    assert result["students"][0]["scores"] == (80, 90) and "new" not in result["tags"]
    print("Изменение исходных коллекций не изменило замороженный результат.")
    try:
        cast(Any, result)["students"][0]["name"] = "Дана"  # Проверка запрета записи.
    except TypeError:
        print("Запись во вложенный словарь: TypeError")
    else:
        raise AssertionError("ожидался запрет записи")
    assert freeze([]) == () and freeze(set()) == frozenset() and dict(freeze({})) == {}
    assert freeze((1, [2, 3])) == (1, (2, 3))
    assert freeze(result) == result
    shared = [1, 2]
    frozen_shared = freeze([shared, shared])
    assert frozen_shared[0] is frozen_shared[1]
    print(
        "Повторная ссылка на подсписок сохранена:", frozen_shared[0] is frozen_shared[1]
    )
    cycle: list[Any] = []
    cycle.append(cycle)
    for value, expected in ((cycle, ValueError), (bytearray(b"abc"), TypeError)):
        try:
            freeze(value)
        except expected as exc:
            print("Граничная проверка:", type(exc).__name__)
        else:
            raise AssertionError("ожидалось исключение")
    print("Пустые контейнеры, вложенный tuple и повторная заморозка проверены.")
