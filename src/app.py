import json
from wsgiref import simple_server

import falcon


class ProposalsResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        # TODO: заглушка
        resp.body = json.dumps({'proposals': []})


api = falcon.API()

proposals = ProposalsResource()
api.add_route('/proposals', proposals)


if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()
