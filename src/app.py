from operator import attrgetter, methodcaller
from wsgiref import simple_server

import falcon

from config import VIA_3_KEY, VIA_OW_KEY
from schemas import ProposalSchema
from storage import Storage
from utils import jsonify


class ProposalsResource:
    def __init__(self, storage):
        self.storage = storage

    def on_get(self, req, resp):
        allowed_order_keys = (
            'adult_prize',
            'child_prize',
            'infant_prize',
            'duration',
            'optimality',
        )
        # Параметры.
        limit = req.get_param_as_int('limit', min=0)
        reverse = req.get_param_as_bool('reverse') or False
        order_by_key = req.get_param('order_by')
        if order_by_key not in allowed_order_keys:
            order_by_key = None

        data = self.storage.get_all_proposals()
        proposals = data.proposals
        if order_by_key:
            if order_by_key == 'optimality':
                key = methodcaller(
                    'calc_optimality',
                    min_prize=data.min_prize,
                    min_duration=data.min_duration)
                # Для оптимальности reverse имеет противоположное значение,
                # так как сортируем от большей оптимальности к меньшей.
                reverse = not reverse
            else:
                key = attrgetter(order_by_key)
            proposals = data.order_by(key=key, reverse=reverse)

        proposals_schema = ProposalSchema(strict=True, many=True)
        result = proposals_schema.dump(proposals[:limit])

        resp.status = falcon.HTTP_200
        resp.body = jsonify({'proposals': result.data})


class DifferenceResource:
    def __init__(self, storage):
        self.storage = storage

    def on_get(self, req, resp):
        allowed_order_keys = (
            'adult_prize',
            'child_prize',
            'infant_prize',
            'duration',
        )
        # Параметры.
        reverse = req.get_param_as_bool('reverse') or False
        order_by_key = req.get_param('order_by', required=True)
        if order_by_key not in allowed_order_keys:
            resp.status = falcon.HTTP_400
            return

        data = self.storage.get_proposals()
        key = attrgetter(order_by_key)
        # Лучшее предложение из первого запроса
        via3 = data[VIA_3_KEY].order_by(key=key, reverse=reverse)[0]
        # Лучшее предложение из второго запроса
        via_ow = data[VIA_OW_KEY].order_by(key=key, reverse=reverse)[0]
        # Сравнение предложений
        result = {
            'adult_prize_diff': via_ow.adult_prize - via3.adult_prize,
            'child_prize_diff': via_ow.child_prize - via3.child_prize,
            'infant_prize_diff': via_ow.infant_prize - via3.infant_prize,
            'duration_diff': via_ow.duration - via3.duration,
            'via3_segments_airports': via3.segments_airports,
            'via_ow_segments_airports': via_ow.segments_airports,
        }

        resp.status = falcon.HTTP_200
        resp.body = jsonify(result)


api = falcon.API()
# Инициализируем хранилище.
storage = Storage()
storage.load()
# Роутинг.
proposals_resource = ProposalsResource(storage)
difference_resource = DifferenceResource(storage)
api.add_route('/proposals', proposals_resource)
api.add_route('/difference', difference_resource)


if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()
