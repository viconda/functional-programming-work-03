"""Проверка двух учебных примеров из лабораторной работы 3."""

from dataclasses import dataclass, replace
from enum import Enum
from functools import reduce
import sys
from typing import Callable


@dataclass(frozen=True)
class Interval:
    """Отрезок с проверкой порядка границ при создании."""

    start: float
    end: float

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError(f"начало {self.start} больше конца {self.end}")

    @property
    def length(self) -> float:
        """Вернуть длину отрезка."""
        return self.end - self.start


class Status(Enum):
    """Состояние студента."""

    ACTIVE = "обучается"
    ACADEMIC_LEAVE = "академический отпуск"


@dataclass(frozen=True)
class Student:
    """Неизменяемая запись студента."""

    id: int
    name: str
    grades: tuple[int, ...] = ()
    status: Status = Status.ACTIVE

    @property
    def gpa(self) -> float:
        """Средний балл, округлённый до десятых."""
        return round(sum(self.grades) / len(self.grades), 1) if self.grades else 0.0


@dataclass(frozen=True)
class Group:
    """Группа с кортежем студентов."""

    code: str
    students: tuple[Student, ...] = ()


def add_student(group: Group, student: Student) -> Group:
    """Добавить студента в новую версию группы."""
    if any(s.id == student.id for s in group.students):
        raise ValueError(f"студент {student.id} уже в группе")
    return replace(group, students=group.students + (student,))


def grade(group: Group, student_id: int, value: int) -> Group:
    """Добавить оценку, сохранив исходные записи."""
    if not 0 <= value <= 100:
        raise ValueError("оценка должна находиться в пределах от 0 до 100")
    if not any(s.id == student_id for s in group.students):
        raise KeyError(student_id)
    return replace(group, students=tuple(
        replace(s, grades=s.grades + (value,)) if s.id == student_id else s
        for s in group.students
    ))


def transfer(source: Group, target: Group, student_id: int) -> tuple[Group, Group]:
    """Перевести студента между двумя группами без изменения оригиналов."""
    if source.code == target.code:
        raise ValueError("нужны две различные группы")
    student = next((s for s in source.students if s.id == student_id), None)
    if student is None:
        raise KeyError(student_id)
    new_target = add_student(target, student)
    new_source = replace(source, students=tuple(
        s for s in source.students if s.id != student_id
    ))
    return new_source, new_target


def ranking(group: Group) -> list[tuple[str, float]]:
    """Рейтинг студентов по убыванию среднего балла."""
    return sorted(((s.name, s.gpa) for s in group.students), key=lambda t: -t[1])


def interval_demo() -> None:
    """Выполнить пример с допустимым и ошибочным отрезком."""
    interval = Interval(2, 5)
    print("Interval(2, 5).length =", interval.length)
    assert interval.length == 3
    assert Interval(2, 2).length == 0
    try:
        Interval(5, 2)
    except ValueError as error:
        print("Interval(5, 2): ValueError:", error)
    else:
        raise AssertionError("неверные границы должны быть отклонены")
    print("assert: обычный отрезок, точка и неверные границы проверены")


def group_demo() -> None:
    """Выполнить свёртку с историей и проверить перевод студента."""
    ops: tuple[Callable[[Group], Group], ...] = (
        lambda g: add_student(g, Student(1, "Аскар")),
        lambda g: add_student(g, Student(2, "Мадина")),
        lambda g: grade(g, 1, 85),
        lambda g: grade(g, 2, 97),
        lambda g: grade(g, 1, 78),
    )
    initial: tuple[Group, ...] = (Group("CS-24-1"),)
    history = reduce(lambda hist, op: hist + (op(hist[-1]),), ops, initial)
    print("Рейтинг:", ranking(history[-1]))
    print("Версий:", len(history), "| студентов в версии 1:",
          len(history[1].students))
    print("Мадина общая в версиях 2 и 3:",
          history[2].students[1] is history[3].students[1])
    print("Мадина общая в версиях 3 и 4:",
          history[3].students[1] is history[4].students[1])
    assert ranking(history[-1]) == [("Мадина", 97.0), ("Аскар", 81.5)]
    assert history[0].students == () and history[1].students[0].grades == ()
    assert history[2].students[1] is history[3].students[1]
    assert history[3].students[1] is not history[4].students[1]
    target = Group("CS-24-2")
    source_new, target_new = transfer(history[-1], target, 1)
    print("Перевод Аскара:", source_new.code, "->", target_new.code)
    print("Размеры групп после перевода:", len(source_new.students),
          len(target_new.students))
    assert len(history[-1].students) == 2 and target.students == ()
    assert target_new.students[0] is history[-1].students[0]
    assert len(source_new.students) == 1 and len(history) == 6
    print("assert: рейтинг, история, структурное разделение и перевод проверены")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interval":
        interval_demo()
    else:
        group_demo()
