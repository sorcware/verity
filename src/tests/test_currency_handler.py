
from src import currency_handler


def test_convert_to_universal_currency():
    input = 87.82
    result = currency_handler.convert_to_universal_currency(input)
    assert result == 8782


def test_whole_number():
    input = 123
    result = currency_handler.convert_to_universal_currency(input)
    assert result == input


def test_negative_number():
    input = -123.45
    result = currency_handler.convert_to_universal_currency(input)
    print(result)
    assert result == -12345
