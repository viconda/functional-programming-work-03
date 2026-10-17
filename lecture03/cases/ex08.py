"""Пример 8. Операции frozenset и использование множества как ключа."""


def run() -> None:
    """Проверить все четыре операции множеств и независимость от порядка."""
    python_devs = frozenset({"Айдос", "Мадина", "Олжас"})
    java_devs = frozenset({"Мадина", "Тимур"})
    print(sorted(python_devs & java_devs))
    print(sorted(python_devs | java_devs))
    teams = {python_devs: "backend", java_devs: "mobile"}
    print(teams[frozenset({"Тимур", "Мадина"})])
    print("Разность:", sorted(python_devs - java_devs))
    print("Симметрическая разность:", sorted(python_devs ^ java_devs))
    assert python_devs & java_devs == frozenset({"Мадина"})
    assert python_devs - java_devs == frozenset({"Айдос", "Олжас"})
    assert len(python_devs) == 3 and not hasattr(python_devs, "add")
