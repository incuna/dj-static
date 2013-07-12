# -*- coding: utf-8 -*-

import static

from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
from django.core.handlers.base import get_path_info
try:
    from urllib.parse import urlparse
except ImportError:     # Python 2
    from urlparse import urlparse
from django.contrib.staticfiles import utils


class StaticFilesHandler(WSGIHandler):
    """WSGI middleware that intercepts calls to the static files
    directory, as defined by the STATIC_URL setting, and serves those files.
    """
    def __init__(self, application, base_dir=None):
        self.application = application
        if not base_dir:
            base_dir = self.get_base_dir()
        self.base_url = urlparse(self.get_base_url())

        self.cling = static.Cling(base_dir)

        super(StaticFilesHandler, self).__init__()

    def get_base_dir(self):
        return settings.STATIC_ROOT

    def get_base_url(self):
        utils.check_settings()
        return settings.STATIC_URL

    def _transpose_environ(self, environ):
        """Translates a given environ to static.Cling's expectations."""
        environ['PATH_INFO'] = environ['PATH_INFO'][len(self.base_url) + 1:]
        return environ

    def _should_handle(self, path):
        """Checks if the path should be handled. Ignores the path if:

        * the host is provided as part of the base_url
        * the request's path isn't under the media path (or equal)
        """
        return path.startswith(self.base_url[2]) and not self.base_url[1]

    def __call__(self, environ, start_response):
        if not self._should_handle(get_path_info(environ)):
            return self.application(environ, start_response)
        environ = self._transpose_environ(environ)
        return self.cling(environ, start_response)