"""Пример 3. Позиционные, вариативные и только именованные параметры."""

from typing import Any, cast


def make_report(
    title: str,
    /,
    *rows: tuple[Any, ...],
    sep: str = " | ",
    upper: bool = False,
    **meta: Any,
) -> str:
    """Сформировать отчёт, сохраняя порядок строк и сортируя метаданные."""
    head = title.upper() if upper else title
    body = [sep.join(map(str, r)) for r in rows]
    tail = [f"{k}: {v}" for k, v in sorted(meta.items())]
    return "\n".join([head, *body, *tail])


def run() -> None:
    """Выполнить пример лекции и проверить запрет передачи title по имени."""
    result = make_report(
        "Итоги", (1, "Алиев", 92), (2, "Ким", 88), upper=True, author="М.Б.", year=2026
    )
    print(result)
    assert result == "ИТОГИ\n1 | Алиев | 92\n2 | Ким | 88\nauthor: М.Б.\nyear: 2026"
    assert make_report("x", (1, 2), sep=";") == "x\n1;2"
    try:
        cast(Any, make_report)(title="Ошибка")  # Намеренная проверка неверного вызова.
    except TypeError:
        print("title= без позиционного заголовка: TypeError, как ожидалось")
    else:
        raise AssertionError("позиционный параметр не был проверен")
