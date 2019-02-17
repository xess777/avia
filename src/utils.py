import json
from datetime import datetime
from decimal import Decimal
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


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            result = float(o)
        else:
            result = super().default(o)

        return result


def jsonify(data):
    return json.dumps(data, cls=ExtendedJSONEncoder, indent=2, sort_keys=True)
