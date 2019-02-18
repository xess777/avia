import unittest

from falcon import testing

import app


class BaseTestCase(testing.TestCase):
    def setUp(self):
        super().setUp()
        self.app = app.get_app()


class TestApp(BaseTestCase):
    def test_difference(self):
        expected = {
            'adult_prize_diff': -164.1,
            'child_prize_diff': -526.8,
            'duration_diff': -15,
            'infant_prize_diff': -202.1,
            'first_segments_airports': ['DXB', 'DEL', 'BKK'],
            'second_segments_airports': ['DXB', 'DEL', 'BKK'],
        }
        params = {
            'order_by': 'adult_prize',
        }
        result = self.simulate_get('/difference', params=params)

        self.assertEqual(result.json, expected)

    def test_proposals(self):
        expected_flights = {
            'onward': [
                {
                    'arrival_timestamp': '2018-10-27T0445',
                    'carrier_id': 'AI',
                    'departure_timestamp': '2018-10-27T0005',
                    'destination': 'DEL',
                    'fare_basis': '2820303decf751-5511-447a-aeb1-810a6b10ad7d@@$255_DXB_DEL_996_9_00:05_$255_DEL_BKK_332_9_13:25__A2_1_1',
                    'number': 996,
                    'number_of_stops': 0,
                    'source': 'DXB',
                    'ticket_type': 'E',
                    'trip_class': 'G',
                    'warning_text': ''
                },
                {
                    'arrival_timestamp': '2018-10-27T1920',
                    'carrier_id': 'AI',
                    'departure_timestamp': '2018-10-27T1325',
                    'destination': 'BKK',
                    'fare_basis': '2820303decf751-5511-447a-aeb1-810a6b10ad7d@@$255_DXB_DEL_996_9_00:05_$255_DEL_BKK_332_9_13:25__A2_1_1',
                    'number': 332,
                    'number_of_stops': 0,
                    'source': 'DEL',
                    'ticket_type': 'E',
                    'trip_class': 'G',
                    'warning_text': ''
                }
            ],
            'returned': []
        }
        expected_pricing = [
            {
                'base_fare': 167.0,
                'taxes': 215.7,
                'total_amount': 382.7,
                'type': 'single_adult'
            },
            {
                'base_fare': 129.0,
                'taxes': 215.7,
                'total_amount': 344.7,
                'type': 'single_infant'
            },
            {
                'base_fare': 20.0,
                'taxes': 0.0,
                'total_amount': 20.0,
                'type': 'single_child'
            }
        ]
        params = {
            'order_by': 'adult_prize',
            'limit': 1,
        }
        result = self.simulate_get('/proposals', params=params)
        result = result.json['proposals'][0]

        self.assertEqual(result['flights'], expected_flights)
        self.assertEqual(result['pricing'], expected_pricing)


if __name__ == '__main__':
        unittest.main()
