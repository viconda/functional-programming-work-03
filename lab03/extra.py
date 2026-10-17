"""Дополнительное задание. Декоратор обычного неизменяемого класса."""

from collections.abc import Callable
from dataclasses import FrozenInstanceError, dataclass, replace
from functools import wraps
from inspect import Parameter, signature
from typing import Any, TypeVar, cast

T = TypeVar("T")


def immutable(cls: type[T]) -> type[T]:
    """Запретить обычные изменения после init и добавить evolve.

    Контракт: обычный класс с __dict__, без вариативных параметров init.
    Каждый параметр конструктора хранится в одноимённом атрибуте.
    evolve вызывает конструктор заново, поэтому повторяет валидацию.
    Защита поверхностная, как frozen=True, а не барьер безопасности.
    """
    original_init = cls.__init__
    parameters = tuple(signature(original_init).parameters.values())[1:]
    if any(
        p.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD) for p in parameters
    ):
        raise TypeError("immutable не поддерживает *args и **kwargs в init")
    if "__slots__" in cls.__dict__:
        raise TypeError("Эта учебная реализация требует обычный __dict__")
    names = frozenset(p.name for p in parameters)
    if "_immutable_ready" in names:
        raise TypeError("Имя _immutable_ready зарезервировано декоратором")

    @wraps(original_init)
    def init(self: T, *args: Any, **kwargs: Any) -> None:
        """Разрешить присваивания только во время первого создания."""
        if getattr(self, "_immutable_ready", False):
            raise FrozenInstanceError("Повторный вызов init запрещён")
        original_init(self, *args, **kwargs)
        if any(not hasattr(self, name) for name in names):
            raise TypeError("Параметры init должны храниться в атрибутах")
        object.__setattr__(self, "_immutable_ready", True)

    def set_attribute(self: T, name: str, value: object) -> None:
        """После создания запретить и изменение, и добавление атрибутов."""
        if getattr(self, "_immutable_ready", False):
            raise FrozenInstanceError(f"Нельзя присвоить атрибут {name}")
        object.__setattr__(self, name, value)

    def del_attribute(self: T, name: str) -> None:
        """После создания запретить удаление атрибутов."""
        if getattr(self, "_immutable_ready", False):
            raise FrozenInstanceError(f"Нельзя удалить атрибут {name}")
        object.__delattr__(self, name)

    def evolve(self: T, **changes: object) -> T:
        """Собрать параметры исходного объекта и создать проверенную копию."""
        unknown = changes.keys() - names
        if unknown:
            raise TypeError(f"Неизвестные поля: {', '.join(sorted(unknown))}")
        values = {name: changes.get(name, getattr(self, name)) for name in names}
        positional = [
            values[p.name] for p in parameters if p.kind is Parameter.POSITIONAL_ONLY
        ]
        keyword = {
            p.name: values[p.name]
            for p in parameters
            if p.kind is not Parameter.POSITIONAL_ONLY
        }
        return cls(*positional, **keyword)

    # setattr применяется к объекту класса, а не к замороженному экземпляру.
    for name, method in (
        ("__init__", init),
        ("__setattr__", set_attribute),
        ("__delattr__", del_attribute),
        ("evolve", evolve),
    ):
        setattr(cls, name, method)
    return cls


@immutable
class Wallet:
    """Обычный класс с проверкой баланса, не dataclass."""

    def __init__(self, owner: str, /, amount: int, *, currency: str = "KZT") -> None:
        """Проверить поля и сохранить параметры под теми же именами."""
        if not owner.strip():
            raise ValueError("Имя владельца обязательно")
        if type(amount) is not int or amount < 0:
            raise ValueError("Баланс должен быть целым неотрицательным")
        if currency not in ("KZT", "USD", "EUR"):
            raise ValueError("Неизвестная валюта")
        self.owner = owner
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        """Дать читаемое представление обычного класса для демонстрации."""
        return f"Wallet({self.owner!r}, {self.amount}, currency={self.currency!r})"


@dataclass(frozen=True)
class FrozenWallet:
    """Та же идея со стандартным генератором методов dataclass."""

    owner: str
    amount: int

    def __post_init__(self) -> None:
        """Проверить те же правила баланса у стандартной замороженной записи."""
        if not self.owner.strip() or type(self.amount) is not int or self.amount < 0:
            raise ValueError("Неверные данные кошелька")


def expect_failure(action: Callable[[], object], error: type[Exception]) -> None:
    """Проверить запрещённое действие."""
    try:
        action()
    except error:
        return
    raise AssertionError(f"Ожидалось исключение {error.__name__}")


def main() -> None:
    """Проверить заморозку, новую копию и повторную проверку инвариантов."""
    original = Wallet("Алия", 1000)
    # Метод добавлен динамически; его наличие известно в этой точке запуска.
    evolve = cast(Any, original).evolve
    updated = cast(Wallet, evolve(amount=1500))
    same_fields = cast(Wallet, evolve())
    assert original.amount == 1000 and updated.amount == 1500
    assert original is not updated and original is not same_fields
    assert updated.owner == original.owner and updated.currency == "KZT"
    expect_failure(lambda: setattr(original, "amount", 2000), FrozenInstanceError)
    expect_failure(lambda: setattr(original, "new_field", True), FrozenInstanceError)
    expect_failure(lambda: delattr(original, "owner"), FrozenInstanceError)
    expect_failure(
        lambda: setattr(original, "_immutable_ready", False), FrozenInstanceError
    )
    expect_failure(lambda: Wallet.__init__(original, "Другой", 0), FrozenInstanceError)
    expect_failure(lambda: evolve(amount=-1), ValueError)
    expect_failure(lambda: evolve(unknown=1), TypeError)
    assert original.amount == 1000 and original.owner == "Алия"
    frozen = FrozenWallet("Алия", 1000)
    frozen_updated = replace(frozen, amount=1500)
    assert frozen.amount == 1000 and frozen_updated.amount == 1500
    expect_failure(lambda: replace(frozen, amount=-1), ValueError)
    print("ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ. @immutable")
    print("Исходный объект:", original)
    print("evolve(amount=1500):", updated)
    print("Оригинал после evolve:", original)
    print("Присваивание, добавление, удаление, повторный init: запрещены.")
    print("Неизвестное поле: TypeError; отрицательный баланс: ValueError.")
    print("dataclass + replace:", frozen, "->", frozen_updated)
    print("Оба решения проверяют новые объекты; исходные объекты сохранены.")
    print("Ограничения: вложенные объекты не замораживаются автоматически;")
    print("object.__setattr__ и прямой __dict__ обходят учебную защиту.")
    print("Проверки: OK")


if __name__ == "__main__":
    main()
