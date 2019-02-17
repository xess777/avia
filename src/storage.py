import uuid
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import List

from config import RS_VIA_3_XML, RS_VIA_OW_XML, VIA_3_KEY, VIA_OW_KEY
from models import (
    Pricing, Proposal, Proposals, Carrier, Airport, Flight, Flights,
    PricingTypeEnum)
from parser import Parser


class Storage:
    """Хранилище."""
    def __init__(self):
        self._proposals = {}
        self._airports = {}
        self._carriers = {}

    def load(self) -> None:
        """Загружает данные из xml файлов в хранилище."""
        # Парсим файл RS_Via-3.xml
        content = Path(RS_VIA_3_XML).read_text()
        data = Parser.parse(content)
        self._proposals[VIA_3_KEY] = self._create_proposals(data)
        # Парсим файл RS_ViaOW.xml
        content = Path(RS_VIA_OW_XML).read_text()
        data = Parser.parse(content)
        self._proposals[VIA_OW_KEY] = self._create_proposals(data)
        # Объединяем результаты парсинга.
        proposals = (self._proposals[VIA_3_KEY].proposals +
                     self._proposals[VIA_OW_KEY].proposals)
        self._proposals['all'] = Proposals(proposals=proposals)

    def get_all_proposals(self) -> 'Proposals':
        """Возвращает все предложения о перелетах."""
        return self._proposals['all']

    def get_proposals(self) -> 'Proposals':
        """Возвращает все предложения о перелетах."""
        return self._proposals

    def _create_proposals(self, data: dict) -> 'Proposals':
        """Создает экземпляр Proposals на основе данных из словаря."""
        proposals = []
        for p_dct in data['proposals']:
            onward_flights = self._create_flights(p_dct['onward'])
            returned_flights = self._create_flights(p_dct['returned'])
            pricing = self._create_pricing(p_dct['pricing'])

            flights = Flights(
                onward=onward_flights,
                returned=returned_flights)

            proposal = Proposal(
                uuid=uuid.uuid4(),
                flights=flights,
                pricing=pricing)

            proposals.append(proposal)

        return Proposals(proposals=proposals)

    def _create_carrier(self, carrier_id: str, name: str) -> 'Carrier':
        """Создает экземпляр Carrier."""
        carrier = Carrier(carrier_id=carrier_id, name=name)
        self._carriers[carrier_id] = carrier

        return carrier

    def _create_airport(self, code: str) -> 'Airport':
        """Создает экземпляр Airport."""
        airport = Airport(code=code)
        self._airports[code] = airport

        return airport

    def _create_flights(self, data: List[dict]) -> List['Flight']:
        """Создает список экземпляров Flight на основе данных из словаря."""
        flights = []
        for f_dct in data:
            # Перевозчик.
            carrier = self._carriers.get(f_dct['carrier_id'])
            if carrier is None:
                carrier = self._create_carrier(
                    carrier_id=f_dct['carrier_id'],
                    name=f_dct['carrier'])
            # Аэропорты.
            source = self._carriers.get(f_dct['source'])
            destination = self._carriers.get(f_dct['destination'])
            if source is None:
                source = self._create_airport(code=f_dct['source'])
            if destination is None:
                destination = self._create_airport(
                    code=f_dct['destination'])

            flight = Flight(
                carrier=carrier,
                number=f_dct['flight_number'],
                source=source,
                destination=destination,
                departure_timestamp=f_dct['departure_timestamp'],
                arrival_timestamp=f_dct['arrival_timestamp'],
                trip_class=f_dct['trip_class'],
                number_of_stops=f_dct['number_of_stops'],
                fare_basis=f_dct['fare_basis'],
                warning_text=f_dct['warning_text'] or '',
                ticket_type=f_dct['ticket_type'])

            flights.append(flight)

        return flights

    def _create_pricing(self, data: dict) -> List['Pricing']:
        """Создает список экземпляров Pricing на основе данных из словаря."""
        type_mapper = {
            'SingleAdult': PricingTypeEnum.SINGLE_ADULT,
            'SingleInfant': PricingTypeEnum.SINGLE_CHILD,
            'SingleChild': PricingTypeEnum.SINGLE_INFANT,
        }
        charge_type_mapper = {
            'BaseFare': 'base_fare',
            'AirlineTaxes': 'taxes',
            'TotalAmount': 'total_amount',
        }

        result = []
        # Сгруппируем по типу ценообразования.
        key = itemgetter('type')
        charges = sorted(data['service_charges'], key=key)
        for type_, group in groupby(charges, key=key):
            params = {
                'type': type_mapper.get(type_),
            }
            for charge in group:
                charge_type_key = charge_type_mapper.get(charge['charge_type'])
                params[charge_type_key] = charge['sum']
            result.append(Pricing(**params))

        return result

