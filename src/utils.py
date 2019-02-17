from datetime import datetime
from enum import Enum
from typing import Union


class DateFormat(Enum):
    DEFAULT = '%d-%m-%Y %H:%M:%S'
    TIMESTAMP = '%Y-%m-%dT%H%M'


def str2date(date_string: str, date_format: str) -> Union[datetime, None]:
    """Преобразует строку в дату.
    В случае неудачного преобразования возвращает None.
    """
    try:
        result = datetime.strptime(date_string, date_format)
    except (ValueError, TypeError):
        result = None

    return result


def str2int(int_string: str) -> Union[int, None]:
    """Преобразует строку в целое число.
    В случае неудачного преобразования возвращает None.
    """
    try:
        result = int(int_string)
    except ValueError:
        result = None

    return result
