from wsgiref import simple_server

import falcon

from resources import ProposalsResource, DifferenceResource
from storage import Storage


def create_app(storage: 'Storage') -> 'falcon.API':
    """Создает приложение."""
    api = falcon.API()
    proposals_resource = ProposalsResource(storage)
    difference_resource = DifferenceResource(storage)
    # Роутинг.
    api.add_route('/proposals', proposals_resource)
    api.add_route('/difference', difference_resource)

    return api


def get_app() -> 'falcon.API':
    """Возвращает инстанс приложения."""
    # Инициализируем хранилище, которое хранит результаты парсинга xml.
    # Хранилище инициализируется перед созданием приложения один раз,
    # чтобы не парсить каждый раз xml на новые запросы.
    storage = Storage()
    storage.load()

    return create_app(storage)


if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, get_app())
    httpd.serve_forever()
