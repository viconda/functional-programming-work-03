"""Пример 13. Enum как набор именованных оценок."""

from enum import Enum
from typing import Any, cast


class Grade(Enum):
    """Категории оценки из примера лекции."""

    EXCELLENT = "A"
    GOOD = "B"
    SATISFACTORY = "C"


def to_grade(score: int) -> Grade:
    """Преобразовать балл по трёхуровневой шкале из лекции."""
    return (
        Grade.EXCELLENT
        if score >= 90
        else Grade.GOOD
        if score >= 75
        else Grade.SATISFACTORY
    )


def run() -> None:
    """Проверить пример и границы категорий."""
    print(to_grade(93), to_grade(80).value)
    print(
        "Границы:",
        to_grade(90).value,
        to_grade(89).value,
        to_grade(75).value,
        to_grade(74).value,
    )
    assert to_grade(90) is Grade.EXCELLENT and to_grade(89) is Grade.GOOD
    assert to_grade(75) is Grade.GOOD and to_grade(74) is Grade.SATISFACTORY
    try:
        cast(Any, Grade).GOOD = "X"  # Проверка запрета переопределения члена.
    except AttributeError:
        print("Переопределение Grade.GOOD: AttributeError")
    else:
        raise AssertionError("член Enum нельзя переопределить")
