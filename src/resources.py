from operator import attrgetter, methodcaller
from typing import TYPE_CHECKING

import falcon

from config import VIA_3_KEY, VIA_OW_KEY
from models import compare_proposals
from schemas import ProposalSchema
from utils import jsonify

if TYPE_CHECKING:
    from storage import Storage


class ProposalsResource:
    def __init__(self, storage: 'Storage') -> None:
        self.storage = storage

    def on_get(self, req, resp) -> None:
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
        # Достаем данные со всеми предложениями о перелетах.
        data = self.storage.get_all_proposals()
        proposals = data.proposals
        # Если передан параметр сортировки, сортируем предложения по нему.
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
    def __init__(self, storage: 'Storage') -> None:
        self.storage = storage

    def on_get(self, req, resp) -> None:
        allowed_order_keys = (
            'adult_prize',
            'child_prize',
            'infant_prize',
            'duration',
        )
        # Параметры.
        reverse = req.get_param_as_bool('reverse') or False
        # Параметр сортировки является обязательным,
        # иначе сравнение предложений будет некорректным.
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
        result = compare_proposals(via3, via_ow)

        resp.status = falcon.HTTP_200
        resp.body = jsonify(result)
