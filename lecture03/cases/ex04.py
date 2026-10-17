"""Пример 4. Распаковка позиционных и именованных аргументов."""


def volume(length: float, width: float, height: float) -> float:
    """Вернуть произведение трёх размеров прямоугольного параллелепипеда."""
    return length * width * height


def run() -> None:
    """Сопоставить обычный вызов с распаковкой кортежа и словаря."""
    dims = (2, 3, 4)
    named = {"length": 2, "width": 3, "height": 4}
    print(volume(*dims), volume(**named))
    assert volume(*dims) == volume(**named) == volume(2, 3, 4) == 24
    assert volume(2, 3, 0) == 0
