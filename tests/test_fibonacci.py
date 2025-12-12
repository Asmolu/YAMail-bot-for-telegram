import pytest

from bot.utils import fibonacci


@pytest.mark.parametrize(
    "n, expected",
    [
        (0, 0),
        (1, 1),
        (2, 1),
        (3, 2),
        (5, 5),
        (10, 55),
    ],
)
def test_fibonacci_values(n, expected):
    assert fibonacci(n) == expected


def test_fibonacci_large_index():
    # проверяем, что мемоизация помогает быстро считать значения
    assert fibonacci(30) == 832040


def test_fibonacci_invalid_type():
    with pytest.raises(ValueError):
        fibonacci(3.14)


def test_fibonacci_negative_index():
    with pytest.raises(ValueError):
        fibonacci(-1)