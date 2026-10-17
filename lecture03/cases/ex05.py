"""Пример 5. Намеренно ошибочное изменяемое значение по умолчанию."""


def add_student_bad(name: str, group: list[str] = []) -> list[str]:
    """Показать ошибку: добавление меняет общий объект значения по умолчанию."""
    group.append(name)
    return group


def add_student_good(name: str, group: list[str] | None = None) -> list[str]:
    """Вернуть новый список студентов, не изменяя переданный список."""
    group = [] if group is None else group
    return [*group, name]


def run() -> None:
    """Показать скрытое состояние и проверить исправленный вариант."""
    defaults = add_student_bad.__defaults__
    assert defaults is not None
    defaults[0].clear()  # Сброс только демонстрационного дефекта.
    print(add_student_bad("Асель"))
    print(add_student_bad("Данияр"))
    print(add_student_good("Асель"))
    print(add_student_good("Данияр"))
    original = ["Алия"]
    result = add_student_good("Данияр", original)
    assert original == ["Алия"]
    assert result == ["Алия", "Данияр"] and result is not original
    assert add_student_good("Асель") == add_student_good("Асель") == ["Асель"]
    print("Переданный список сохранён:", original)
