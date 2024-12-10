import urllib.request
import urllib.error
import http.client

import logging
logger = logging.getLogger("gs-scroller.urlread")

try:
    from google.appengine.api.urlfetch_errors import Error as URLFetchError
except ImportError:
    URLFetchError = None

IO_ERRORS = tuple(filter(lambda e: e is not None, (
    http.client.HTTPException,
    urllib.error.URLError,
    URLFetchError,
    IOError, OSError
)))

class HTTPNoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None

urllib.request.install_opener(urllib.request.build_opener(HTTPNoRedirectHandler))

class NotFound(Exception):
    pass

class NotResponding(Exception):
    pass

def urlread(url, timeout=30):
    try:
        reply = urllib.request.urlopen(url, timeout=timeout)
    except urllib.error.HTTPError as error:
        if error.code in {301, 302, 303, 307, 400, 401, 403, 404, 410}:
            raise NotFound
        raise
    except IO_ERRORS: # pylint: disable=catching-non-exception
        raise NotResponding
    return reply.read()

