from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal


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


@dataclass(frozen=True)
class Proposal:
    """Класс предложения по перелету."""
    uuid: str
    flights: 'Flights'
    pricing: List['Pricing']


@dataclass(frozen=True)
class Pricing:
    """Класс ценообразования."""
    type: 'PricingTypeEnum'
    base_fare: 'Decimal' = 0
    taxes: 'Decimal' = 0
    total_amount: 'Decimal' = 0


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
