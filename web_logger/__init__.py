import tornado.web

from web_logger.pages.root import RootHandler
from web_logger.api.container_list import APIContainerListHandler
from web_logger.api.container_log import APIContainerLogHandler


def make_app():
    return tornado.web.Application([
        (r'/', RootHandler),
        (r'/api/container_list', APIContainerListHandler),
        (r'/api/container_log', APIContainerLogHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'web_logger/pages/static'}),
    ], debug=True)
