from wsgiref import simple_server

import falcon

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
        )
        # Параметры.
        limit = req.get_param_as_int('limit', min=0)
        reverse = req.get_param_as_bool('reverse') or False
        order_by_key = req.get_param('order_by')
        if order_by_key not in allowed_order_keys:
            order_by_key = None

        data = self.storage.get_proposals()
        if order_by_key:
            proposals = data.order_by(key=order_by_key, reverse=reverse)
        else:
            proposals = data.proposals

        proposals_schema = ProposalSchema(strict=True, many=True)
        result = proposals_schema.dump(proposals[:limit])

        resp.status = falcon.HTTP_200
        resp.body = jsonify({'proposals': result.data})


api = falcon.API()
# Инициализируем хранилище.
storage = Storage()
storage.load()
# Роутинг.
proposals = ProposalsResource(storage)
api.add_route('/proposals', proposals)


if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()
