"""Дополнение к разделу 5.3. Неизменяемость str и bytes."""

from typing import Any, cast


def run() -> None:
    """Проверить строковые преобразования и запрет изменения байта."""
    text = "  Python  "
    result = text.strip().upper().replace("PYTHON", "Python 3")
    parts = ["функции", "и", "неизменяемость"]
    joined = " ".join(parts)
    payload = b"abc"
    changed = payload.replace(b"a", b"A")
    print("Исходная строка:", repr(text))
    print("После strip/upper/replace:", repr(result))
    print("join:", joined)
    print("split:", joined.split())
    print("bytes:", payload, "новое значение:", changed)
    assert text == "  Python  " and result == "Python 3"
    assert joined.split() == parts
    assert payload == b"abc" and changed == b"Abc"
    for value in (text, payload):
        try:
            cast(Any, value)[0] = 0  # Намеренная проверка запрета записи.
        except TypeError:
            print(type(value).__name__, "не допускает присваивание элементу")
        else:
            raise AssertionError("ожидался неизменяемый тип")
    print("Метод без изменения может вернуть тот же объект; is не является контрактом.")
