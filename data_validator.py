"""
Т.к. в условии сказано "Результат валидации -  bool.", так и сделал.
То есть, валидатор никак не учитывает и не сигнализирует о том, какие именно значения не прошли валидацию
 и возвращает сразу False как только находит первое невалидное значение.
По этому же не делал приведения к типам. Исходные данные никак не меняются.
При написании самих валидаторов исходил из того, что данные из условия удовлетворяют данной схеме валидации.
То есть, что стринг "42" должен проходить валидацию валидатором "int", а стринг с датой проходит валидацию на "date".
"""
from typing import Dict, Tuple
from json import loads
from datetime import datetime

DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def is_str(value: str, *args, **kwargs) -> str:
    if not isinstance(value, str):
        raise TypeError
    return value


def is_date_str(value: str, *args, **kwargs) -> str:
    datetime.strptime(value, kwargs.get('date_format', DEFAULT_DATE_FORMAT)).date()
    return value


def is_datetime_str(value: str, *args, **kwargs) -> str:
    datetime.strptime(value, kwargs.get('datetime_format', DEFAULT_DATETIME_FORMAT))
    return value


def is_numeric(value: str, *args, **kwargs) -> str:
    int(value)  # т.к. не понятно, может ли быть тут отрицательное число, не использовал str.isdigit()
    return value


class DataValidator:
    """
    Реализует класс для валидации данных, с публичным методом check() и атрибутом validators.
    Пример использования:
        price_validator = DataValidator(input_schema, validators=validators)
        is_valid = price_validator.check(input_data)
        price_validator.validators.update({'str': (lambda x: isinstance(x, str), )})
    """

    def __init__(self, schema: str, validators: Dict[str, Tuple[callable]] = None):
        """
        Инициализация методов и атрибутов
        :param schema: схема валидации в виде строки с json-структурой, типа: '{"data_date": "date", ...}'
        :param validators: словарь, в котором ключи - имена валидаторов, значения - кортежы валидирующих функций.
            Параметр опциональный. Полученные валидаторы обновят словарь с базовыми валидаторами.
        """
        self.__base_validators = {
            'int': (is_str, is_numeric),
            'date': (is_str, is_date_str),
            'datetime': (is_str, is_datetime_str)
            # ...
        }
        self.__schema = loads(schema)
        self.validators = {**self.__base_validators, **validators} if validators else self.__base_validators.copy()

    def check(self, data: Dict, *args, **kwargs) -> bool:
        """
        Проверяет занчения в полученном словаре соответствующими валидаторами из схемы.
        В случае если параметра нет в схеме - скипает.
        Если параметр есть в схеме но нет соответствующего валидатора - считает что валидация пройдена.
        """
        for key, value in data.items():
            if key in self.__schema:
                for validator in self.validators.get(self.__schema[key], (lambda x: True,)):
                    try:
                        validator(value, *args, **kwargs)
                    except (TypeError, ValueError):
                        return False
        return True
