"""Вспомогательные функции для бота."""

from functools import lru_cache


@lru_cache(maxsize=None)
def fibonacci(n: int) -> int:
    """Возвращает n-е число Фибоначчи (нумерация с нуля).

    Args:
        n: Позиция числа Фибоначчи, начиная с 0.

    Returns:
        int: Значение числа Фибоначчи на позиции ``n``.

    Raises:
        ValueError: Если ``n`` отрицательное или не является целым числом.
    """

    if not isinstance(n, int):
        raise ValueError("Index must be an integer")
    if n < 0:
        raise ValueError("Index must be non-negative")
    if n in (0, 1):
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)