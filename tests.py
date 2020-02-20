import pytest
from json import dumps
from data_validator import DataValidator, is_str, is_date_str, is_datetime_str, is_numeric


def _test_func(func, test_data, *args, **kwargs):
    for input_param, expected in test_data.items():
        if expected is True:
            assert func(input_param, *args, **kwargs)
        else:
            with pytest.raises(expected):
                func(input_param, *args, **kwargs)


def test_is_str():
    test_data = {1: TypeError, '1': True, 'a': True, 'abc': True}
    _test_func(is_str, test_data)


def test_is_date_str():
    test_data = {1: TypeError, '1': ValueError, '2020-02-07': True, '2020-44-52': ValueError, '01-12-1992': ValueError}
    _test_func(is_date_str, test_data)

    test_data = {'2020-02-07': ValueError, '2020:02:07': True}
    _test_func(is_date_str, test_data, date_format='%Y:%m:%d')


def test_is_datetime_str():
    test_data = {
        1: TypeError, '2020-02-07 16:00:00': True, '2020-222-99 16:00:00': ValueError, '2020:02:99 12:00': ValueError
    }
    _test_func(is_datetime_str, test_data)

    test_data = {'2020-02-07 16:00:00': ValueError, '2020:02:29 12:00': True}
    _test_func(is_datetime_str, test_data, datetime_format='%Y:%m:%d %H:%M')


def test_is_numeric_str():
    test_data = {1: True, '1': True, '-1': True, '6666666666': True, 'test': ValueError}
    _test_func(is_numeric, test_data)


def test_validator_check():
    price_validator = DataValidator(schema=dumps({"data_date": "date"}))
    assert price_validator.check({"data_date": "2020-02-07"})
    assert price_validator.check({"data_date": "2020:02:07"}, date_format='%Y:%m:%d')

    price_validator = DataValidator(schema=dumps({"value": "int"}))
    assert price_validator.check({"value": "42"})
    assert price_validator.check({"price": "48.5"})

    price_validator.validators['int'] = (lambda x: True,)
    assert price_validator.check({"value": "test"})

    price_validator.validators.pop('int')
    assert price_validator.check({"value": "test"})

    test_schema = {
        "data_date": "date",
        "datetime": "datetime",
        "value": "int"
    }
    test_data = {
        "data_date": "2020-02-07",
        "datetime": "2020-02-07 16:00:00",
        "value": "42",
        "price": "48.5"
    }
    price_validator = DataValidator(schema=dumps(test_schema))
    assert price_validator.check(test_data)
