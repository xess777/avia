import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import List

from utils import DateFormat, str2date, str2int


class Parser:
    """Парсер XML."""

    @classmethod
    def parse(cls, content: str) -> dict:
        """Парсит содержимое xml.

        Возвращает словарь вида:
        {
            'request_id': id запроса (Пр.: "123ABCD")
            'request_time': время запроса (Пр.: "28-09-2015 20:23:49")
            'response_time': время ответа (Пр.: "28-09-2015 20:23:56")
            'proposals': список предложений по перелетам
        }
        """
        root = ET.fromstring(content)
        request_time = root.attrib.get('RequestTime')
        response_time = root.attrib.get('ResponseTime')
        request_node = root.find('RequestId')
        date_format = DateFormat.DEFAULT.value

        data = {
            'request_id': request_node.text if request_node else '',
            'request_time': str2date(request_time, date_format=date_format),
            'response_time': str2date(response_time, date_format=date_format),
            'proposals': [],
        }

        for proposal_node in root.findall('*/Flights'):
            onward_node = proposal_node.find('OnwardPricedItinerary')
            return_node = proposal_node.find('ReturnPricedItinerary')
            pricing_node = proposal_node.find('Pricing')

            data['proposals'].append({
                'onward': cls._parse_flights(onward_node),
                'returned': (
                    cls._parse_flights(return_node) if return_node else []),
                'pricing': cls._parse_pricing(pricing_node),
            })

        return data

    @classmethod
    def _parse_flights(cls, node: ET.Element) -> List[dict]:
        """Парсит содержимое тэга Flights.

        Возвращает список словарей вида:
        [
            {
                'carrier_id': id перевозчика,
                'carrier': наименование перевозчика,
                'flight_number': номер рейса,
                'source': аэропорт вылета,
                'destination': аэропорт прибытия,
                'departure_timestamp': время вылета,
                'arrival_timestamp': время прибытия,
                'trip_class': класс,
                'number_of_stops': количество остановок,
                'fare_basis': код FareBasis,
                'warning_text': предупреждение,
                'ticket_type': тип билета,
            },
            ...
        ]
        """
        flights = []
        for flight in node.iter('Flight'):
            carrier_node = flight.find('Carrier')
            flight_number_node = flight.find('FlightNumber')
            source_node = flight.find('Source')
            destination_node = flight.find('Destination')
            departure_ts_node = flight.find('DepartureTimeStamp')
            arrival_ts_node = flight.find('ArrivalTimeStamp')
            class_node = flight.find('Class')
            number_of_stops_node = flight.find('NumberOfStops')
            fare_basis_node = flight.find('FareBasis')
            warning_text_node = flight.find('WarningText')
            ticket_type_node = flight.find('TicketType')

            # В xml файлах встречаются опечатки в тегах.
            if departure_ts_node is None:
                departure_ts_node = flight.find('DeartureTimeStamp')

            flights.append({
                'carrier_id': carrier_node.attrib.get('id'),
                'carrier': carrier_node.text,
                'flight_number': str2int(flight_number_node.text),
                'source': source_node.text,
                'destination': destination_node.text,
                'departure_timestamp': str2date(
                    departure_ts_node.text,
                    date_format=DateFormat.TIMESTAMP.value),
                'arrival_timestamp': str2date(
                    arrival_ts_node.text,
                    date_format=DateFormat.TIMESTAMP.value),
                'trip_class': class_node.text,
                'number_of_stops': str2int(number_of_stops_node.text),
                'fare_basis': fare_basis_node.text.strip(),
                'warning_text': warning_text_node.text,
                'ticket_type': ticket_type_node.text,
            })

        return flights

    @classmethod
    def _parse_pricing(cls, node: ET.Element) -> dict:
        """Парсит содержимое тэга Pricing.

        Возвращает словарь вида:
        {
            'currency': валюта,
            'service_charges': [
                {
                    'type': тип ценообразования,
                    'charge_type': тип сумм,
                    'sum': сумма,
                },
                ...
            ]
        }
        """
        pricing = {
            'currency': node.attrib.get('currency'),
            'service_charges': [],
        }

        for charge_node in node.iter('ServiceCharges'):
            pricing['service_charges'].append({
                'type': charge_node.attrib.get('type'),
                'charge_type': charge_node.attrib.get('ChargeType'),
                'sum': Decimal(charge_node.text) if charge_node.text else 0,
            })

        return pricing
