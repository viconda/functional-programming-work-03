"""Задание 6. Вариант 3, неизменяемый библиотечный абонемент."""

from collections.abc import Callable
from dataclasses import FrozenInstanceError, dataclass, replace
from datetime import date, timedelta
from enum import Enum
from functools import reduce
from typing import TypedDict


class LoanStatus(Enum):
    """Допустимые состояния выдачи."""

    ACTIVE = "на руках"
    RETURNED = "возвращена"


class LibraryReport(TypedDict):
    """Тип независимой итоговой сводки."""

    reader: str
    books: list[tuple[int, str, str, str, int]]
    active: int
    overdue: list[str]
    fine_kzt: int


@dataclass(frozen=True)
class Book:
    """Книга; даже вложенное поле authors неизменяемо."""

    isbn: str
    title: str
    authors: tuple[str, ...]

    def __post_init__(self) -> None:
        """Проверить обязательные поля и неизменяемость списка авторов."""
        if not self.isbn.strip() or not self.title.strip():
            raise ValueError("ISBN и название не могут быть пустыми")
        if type(self.authors) is not tuple or not self.authors:
            raise ValueError("Авторы задаются непустым кортежем")
        if any(not isinstance(a, str) or not a.strip() for a in self.authors):
            raise ValueError("Имя автора не может быть пустым")


@dataclass(frozen=True)
class Loan:
    """Одна выдача; fine выражен целым числом тенге."""

    loan_id: int
    book: Book
    issued_on: date
    due_on: date
    status: LoanStatus = LoanStatus.ACTIVE
    returned_on: date | None = None
    fine: int = 0
    assessed_through: date | None = None

    def __post_init__(self) -> None:
        """Проверить даты, целочисленный штраф и согласованность статуса."""
        if type(self.loan_id) is not int or self.loan_id <= 0:
            raise ValueError("Номер выдачи должен быть положительным целым")
        if type(self.issued_on) is not date or type(self.due_on) is not date:
            raise ValueError("Даты выдачи и возврата должны иметь тип date")
        if self.due_on < self.issued_on:
            raise ValueError("Срок возврата раньше даты выдачи")
        if type(self.fine) is not int or self.fine < 0:
            raise ValueError("Штраф должен быть целым неотрицательным")
        if not isinstance(self.book, Book) or not isinstance(self.status, LoanStatus):
            raise TypeError("Недопустимая книга или статус")
        if (self.status is LoanStatus.RETURNED) != (self.returned_on is not None):
            raise ValueError("Статус возврата должен соответствовать его дате")
        if self.returned_on is not None and (
            type(self.returned_on) is not date or self.returned_on < self.issued_on
        ):
            raise ValueError("Возврат не может предшествовать выдаче")
        if self.assessed_through is not None and (
            type(self.assessed_through) is not date
            or self.assessed_through < self.due_on
        ):
            raise ValueError("Граница начисления не может предшествовать сроку")
        if self.assessed_through is not None and self.returned_on is not None:
            if self.assessed_through > self.returned_on:
                raise ValueError("Нельзя учитывать просрочку после возврата")
        if self.fine > 0 and self.assessed_through is None:
            raise ValueError("Для ненулевого штрафа нужна граница начисления")


@dataclass(frozen=True)
class LibraryCard:
    """Абонемент с историей выдач и лимитом активных книг."""

    number: str
    reader: str
    loans: tuple[Loan, ...] = ()
    limit: int = 3

    def __post_init__(self) -> None:
        """Проверить неизменяемость выдач, уникальность номеров и лимит."""
        if not self.number.strip() or not self.reader.strip():
            raise ValueError("Номер абонемента и имя читателя обязательны")
        if type(self.limit) is not int or self.limit <= 0:
            raise ValueError("Лимит должен быть положительным целым")
        if type(self.loans) is not tuple or any(
            not isinstance(loan, Loan) for loan in self.loans
        ):
            raise ValueError("Выдачи должны храниться в кортеже Loan")
        if len({loan.loan_id for loan in self.loans}) != len(self.loans):
            raise ValueError("Номера выдач должны быть уникальными")
        active = tuple(loan for loan in self.loans if loan.status is LoanStatus.ACTIVE)
        if len(active) > self.limit:
            raise ValueError("Превышен лимит активных книг")
        if len({loan.book.isbn for loan in active}) != len(active):
            raise ValueError("Нельзя выдать ту же книгу повторно до возврата")


def find_loan(card: LibraryCard, loan_id: int, *, active: bool = False) -> Loan:
    """Найти выдачу и при необходимости проверить, что она открыта."""
    loan = next((item for item in card.loans if item.loan_id == loan_id), None)
    if loan is None:
        raise KeyError(f"Выдача {loan_id} не найдена")
    if active and loan.status is not LoanStatus.ACTIVE:
        raise ValueError("Книга уже возвращена")
    return loan


def with_loan(card: LibraryCard, updated: Loan) -> LibraryCard:
    """Заменить одну выдачу, разделяя остальные объекты с предыдущей версией."""
    return replace(
        card,
        loans=tuple(
            updated if loan.loan_id == updated.loan_id else loan for loan in card.loans
        ),
    )


def issue(card: LibraryCard, book: Book, on: date, due: date) -> LibraryCard:
    """Выдать книгу; валидация нового абонемента проверяет лимит и дубликаты."""
    new_id = max((loan.loan_id for loan in card.loans), default=0) + 1
    return replace(card, loans=card.loans + (Loan(new_id, book, on, due),))


def return_book(card: LibraryCard, loan_id: int, on: date) -> LibraryCard:
    """Закрыть выдачу без изменения уже начисленного штрафа."""
    loan = find_loan(card, loan_id, active=True)
    if loan.assessed_through is not None and on < loan.assessed_through:
        raise ValueError("Возврат не может быть раньше уже учтённой просрочки")
    return with_loan(card, replace(loan, status=LoanStatus.RETURNED, returned_on=on))


def extend(card: LibraryCard, loan_id: int, *, on: date, days: int) -> LibraryCard:
    """Продлить открытую выдачу до наступления просрочки."""
    loan = find_loan(card, loan_id, active=True)
    if type(days) is not int or days <= 0:
        raise ValueError("Продление должно быть положительным целым числом дней")
    if not loan.issued_on <= on <= loan.due_on:
        raise ValueError("Продление допустимо со дня выдачи до срока возврата")
    return with_loan(card, replace(loan, due_on=loan.due_on + timedelta(days=days)))


def charge_fine(
    card: LibraryCard, loan_id: int, *, on: date, daily_rate: int = 100
) -> LibraryCard:
    """Начислить штраф за ещё не учтённые дни; после возврата долг не растёт."""
    loan = find_loan(card, loan_id)
    if type(daily_rate) is not int or daily_rate < 0:
        raise ValueError("Ставка штрафа должна быть целым неотрицательным числом")
    if on < loan.issued_on:
        raise ValueError("Начисление не может предшествовать выдаче")
    through = min(on, loan.returned_on) if loan.returned_on else on
    previous = loan.assessed_through or loan.due_on
    days = max(0, (through - previous).days)
    assessed = (
        max(previous, through) if through > loan.due_on else loan.assessed_through
    )
    return with_loan(
        card,
        replace(loan, fine=loan.fine + days * daily_rate, assessed_through=assessed),
    )


def report(card: LibraryCard, *, on: date) -> LibraryReport:
    """Собрать независимую сводку включениями и сортировкой с lambda."""
    rows = [
        (
            loan.loan_id,
            loan.book.title,
            loan.status.value,
            loan.due_on.isoformat(),
            loan.fine,
        )
        for loan in card.loans
    ]
    active = [loan for loan in card.loans if loan.status is LoanStatus.ACTIVE]
    return {
        "reader": card.reader,
        "books": sorted(rows, key=lambda row: (row[3], row[1])),
        "active": len(active),
        "overdue": [loan.book.title for loan in active if loan.due_on < on],
        "fine_kzt": sum(loan.fine for loan in card.loans),
    }


def must_fail(action: Callable[[], object], error: type[Exception]) -> None:
    """Проверить ожидаемый отказ, не подавляя неожиданные исключения."""
    try:
        action()
    except error:
        return
    raise AssertionError(f"Ожидалось исключение {error.__name__}")


def main() -> None:
    """Построить историю reduce и выполнить положительные и граничные тесты."""
    first = Book("9780132350884", "Чистый код", ("Роберт Мартин",))
    second = Book("9781491946008", "Изучаем Python", ("Марк Лутц",))
    start = LibraryCard("LIB-003", "Читатель № 3")
    operations: tuple[Callable[[LibraryCard], LibraryCard], ...] = (
        lambda card: issue(card, first, date(2026, 10, 1), date(2026, 10, 10)),
        lambda card: issue(card, second, date(2026, 10, 2), date(2026, 10, 12)),
        lambda card: extend(card, 1, on=date(2026, 10, 8), days=5),
        lambda card: return_book(card, 2, date(2026, 10, 11)),
        lambda card: charge_fine(card, 1, on=date(2026, 10, 17)),
    )
    initial_history: tuple[LibraryCard, ...] = (start,)
    history = reduce(
        lambda versions, op: versions + (op(versions[-1]),), operations, initial_history
    )
    final = history[-1]
    assert len(history) == 6 and start.loans == ()
    assert history[2].loans[0].due_on == date(2026, 10, 10)
    assert final.loans[0].due_on == date(2026, 10, 15)
    assert history[2].loans[1] is history[3].loans[1]
    assert history[3].loans[0] is history[4].loans[0]
    assert final.loans[0].book is first and final.loans[0].fine == 200
    assert report(final, on=date(2026, 10, 17))["fine_kzt"] == 200
    assert charge_fine(final, 1, on=date(2026, 10, 17)) == final
    assert charge_fine(final, 1, on=date(2026, 10, 18)).loans[0].fine == 300
    assert charge_fine(history[1], 1, on=date(2026, 10, 10)).loans[0].fine == 0
    assert extend(history[1], 1, on=date(2026, 10, 10), days=1).loans[0].due_on == date(
        2026, 10, 11
    )
    assert charge_fine(final, 1, on=date(2026, 10, 16)) == final
    returned = return_book(final, 1, date(2026, 10, 18))
    assert charge_fine(returned, 1, on=date(2026, 10, 20)).loans[0].fine == 300
    assert charge_fine(returned, 2, on=date(2026, 10, 20)).loans[1].fine == 0
    must_fail(lambda: Book("", "Книга", ("Автор",)), ValueError)
    must_fail(lambda: Loan(1, first, date(2026, 10, 2), date(2026, 10, 1)), ValueError)
    must_fail(lambda: replace(final.loans[0], fine=-1), ValueError)
    must_fail(lambda: replace(start, limit=0), ValueError)
    must_fail(
        lambda: issue(final, first, date(2026, 10, 17), date(2026, 10, 20)), ValueError
    )
    must_fail(lambda: replace(history[2], limit=1), ValueError)
    must_fail(lambda: return_book(final, 99, date(2026, 10, 17)), KeyError)
    must_fail(lambda: return_book(final, 2, date(2026, 10, 17)), ValueError)
    must_fail(lambda: return_book(final, 1, date(2026, 10, 16)), ValueError)
    must_fail(lambda: extend(final, 1, on=date(2026, 10, 17), days=1), ValueError)
    must_fail(lambda: extend(history[1], 1, on=date(2026, 10, 5), days=0), ValueError)
    must_fail(
        lambda: charge_fine(final, 1, on=date(2026, 10, 18), daily_rate=-1), ValueError
    )
    must_fail(lambda: setattr(final, "reader", "Другой читатель"), FrozenInstanceError)
    print("ЗАДАНИЕ 6. Вариант 3. Библиотечный абонемент")
    for index, card in enumerate(history):
        print(
            f"Версия {index}: выдач {len(card.loans)}, "
            f"штраф {sum(loan.fine for loan in card.loans)} KZT"
        )
    summary = report(final, on=date(2026, 10, 17))
    print("Итоговая сводка:")
    for row in summary["books"]:
        print(row)
    print(f"На руках: {summary['active']}; долг: {summary['fine_kzt']} KZT")
    print(
        "Неизменённая выдача разделяется версиями 2 и 3:",
        history[2].loans[1] is history[3].loans[1],
    )
    print("Исходный абонемент пуст:", start.loans == ())
    print("Повторный штраф не дублирует долг; после возврата долг не растёт.")
    print("Проверки операций, инвариантов и граничных случаев: OK")


if __name__ == "__main__":
    main()
