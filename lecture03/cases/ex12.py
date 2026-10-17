"""Пример 12. Представление словаря только для чтения."""

from types import MappingProxyType
from typing import Any, cast


def run() -> None:
    """Проверить запрет записи через proxy и видимость записи через оригинал."""
    _settings = {"lang": "ru", "theme": "dark"}
    SETTINGS = MappingProxyType(_settings)
    print(SETTINGS["lang"])
    try:
        cast(Any, SETTINGS)["lang"] = "kk"  # Проверка запрета записи.
    except TypeError as exc:
        print("Нельзя изменить:", exc)
    else:
        raise AssertionError("представление должно запрещать запись")
    _settings["lang"] = "kk"
    print("После изменения исходного словаря:", SETTINGS["lang"])
    assert SETTINGS["lang"] == "kk"
