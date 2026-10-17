"""Пример 11. Замороженный счёт и чистое пополнение."""

from dataclasses import dataclass, replace, FrozenInstanceError, field
from typing import Any, cast


@dataclass(frozen=True)
class Account:
    """Неизменяемое состояние счёта с историей операций."""

    owner: str
    balance: float = 0.0
    history: tuple[tuple[str, float], ...] = field(default_factory=tuple)


def deposit(acc: Account, amount: float) -> Account:
    """Чистая функция: возвращает новое состояние счёта."""
    if amount <= 0:
        raise ValueError("сумма должна быть положительной")
    return replace(
        acc, balance=acc.balance + amount, history=acc.history + (("deposit", amount),)
    )


def run() -> None:
    """Сохранить старые версии и проверить запрет присваивания полю."""
    a0 = Account("Нурлан")
    a1 = deposit(a0, 5000)
    a2 = deposit(a1, 1500)
    print(a0)
    print(a2)
    try:
        cast(Any, a2).balance = 1_000_000  # Намеренная проверка заморозки.
    except FrozenInstanceError as exc:
        print("Ошибка:", type(exc).__name__)
    else:
        raise AssertionError("счёт должен быть заморожен")
    assert a0.balance == 0.0 and a1.balance == 5000.0 and a2.balance == 6500.0
    assert len(a0.history) == 0 and len(a1.history) == 1 and len(a2.history) == 2
    for amount in (0, -10):
        try:
            deposit(a0, amount)
        except ValueError:
            pass
        else:
            raise AssertionError("неположительное пополнение запрещено")
