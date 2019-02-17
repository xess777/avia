from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from operator import attrgetter
from typing import List, Union

from cached_property import cached_property


class PricingTypeEnum(Enum):
    """Типы ценообразования."""
    # Один взрослый.
    SINGLE_ADULT = 0
    # Один ребенок.
    SINGLE_CHILD = 1
    # Один младенец.
    SINGLE_INFANT = 2


@dataclass(frozen=True)
class Proposals:
    """Класс для хранения предложений по перелетам."""
    proposals: List['Proposal']

    def order_by(self, key, reverse=False):
        """Возвращает отсортированный по ключу список предложений."""
        return sorted(self.proposals, key=attrgetter(key), reverse=reverse)


@dataclass(frozen=True)
class Proposal:
    """Класс предложения по перелету."""
    uuid: str
    flights: 'Flights'
    pricing: List['Pricing']

    @cached_property
    def adult_prize(self):
        """Итоговая стоимость для одного взрослого."""
        pricing = self._get_pricing_by_type(PricingTypeEnum.SINGLE_ADULT)
        result = pricing.total_amount if pricing else Decimal()

        return result

    @cached_property
    def child_prize(self):
        """Итоговая стоимость для одного ребенка."""
        pricing = self._get_pricing_by_type(PricingTypeEnum.SINGLE_CHILD)
        # Если такого типа нет, возвращаем стоимость как за взрослого.
        result = pricing.total_amount if pricing else self.adult_prize

        return result

    @cached_property
    def infant_prize(self):
        """Итоговая стоимость для одного младенца."""
        pricing = self._get_pricing_by_type(PricingTypeEnum.SINGLE_INFANT)
        # Если такого типа нет, возвращаем стоимость как за взрослого.
        result = pricing.total_amount if pricing else self.adult_prize

        return result

    @cached_property
    def duration(self):
        """Продолжительность полета в минутах."""
        result = None
        flights = self.flights.onward
        if flights:
            # Время вылета из начального пункта.
            departure_ts = flights[0].departure_timestamp
            # Время прилета в конечный пункт.
            arrival_ts = flights[-1].arrival_timestamp
            # Разница в минутах.
            result = (arrival_ts - departure_ts).total_seconds() // 60

        return result

    def _get_pricing_by_type(self, type_) -> Union['Pricing', None]:
        """Возвращает экземпляр Pricing по типу из списка ценообразований.

        Может вернуть None, если нужный тип не найден.
        """
        result = None
        for item in self.pricing:
            if item.type == type_:
                result = item
                break

        return result


@dataclass(frozen=True)
class Pricing:
    """Класс ценообразования."""
    type: 'PricingTypeEnum'
    base_fare: 'Decimal' = 0
    taxes: 'Decimal' = 0
    total_amount: 'Decimal' = 0

    @property
    def type_name(self) -> str:
        return self.type.name.lower()


@dataclass(frozen=True)
class Carrier:
    """Класс с данными о перевозчике."""
    carrier_id: str
    name: str


@dataclass(frozen=True)
class Airport:
    """Класс с данными о аэропорте."""
    code: str


@dataclass(frozen=True)
class Flights:
    """Класс с данными о перелетах."""
    onward: List['Flight']
    returned: List['Flight']


@dataclass(frozen=True)
class Flight:
    """Класс с данными о сегменте перелета."""
    carrier: 'Carrier'
    number: int
    source: 'Airport'
    destination: 'Airport'
    departure_timestamp: datetime
    arrival_timestamp: datetime
    trip_class: str
    number_of_stops: int
    fare_basis: str
    warning_text: str
    ticket_type: str

    @property
    def carrier_id(self) -> str:
        return self.carrier.carrier_id if self.carrier else ''

    @property
    def carrier_name(self) -> str:
        return self.carrier.carrier_name if self.carrier else ''

    @property
    def source_code(self) -> str:
        return self.source.code if self.source else ''

    @property
    def destination_code(self) -> str:
        return self.destination.code if self.destination else ''
