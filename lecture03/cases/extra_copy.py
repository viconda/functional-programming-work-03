"""Дополнение к разделу 8. Поверхностное и глубокое копирование."""

from copy import copy, deepcopy
from typing import Any


def run() -> None:
    """Изменить вложенный список и сравнить поведение двух видов копий."""
    original: dict[str, Any] = {"scores": [80, 90], "name": "Алия"}
    shallow = copy(original)
    deep = deepcopy(original)
    print("Внешние словари различны:", original is not shallow is not deep)
    print("Вложенный список общий с shallow:", original["scores"] is shallow["scores"])
    print("Вложенный список общий с deep:", original["scores"] is deep["scores"])
    shallow["scores"].append(100)
    print("Оригинал после изменения shallow:", original)
    print("Глубокая копия:", deep)
    assert original == {"scores": [80, 90, 100], "name": "Алия"}
    assert deep == {"scores": [80, 90], "name": "Алия"}
    shallow["name"] = "Дана"
    assert original["name"] == "Алия"
    print("Замена внешнего поля shallow не меняет поле оригинала.")
