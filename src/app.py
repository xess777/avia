from wsgiref import simple_server

import falcon

from schemas import ProposalSchema
from storage import Storage
from utils import jsonify


class ProposalsResource:
    def __init__(self, storage):
        self.storage = storage

    def on_get(self, req, resp):
        # Параметры.
        limit = req.get_param_as_int('limit', min=0)

        proposals = self.storage.get_proposals()
        proposals_schema = ProposalSchema(strict=True, many=True)
        result = proposals_schema.dump(proposals.proposals[:limit])

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
