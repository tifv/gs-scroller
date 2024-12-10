import urllib.request
import urllib.error
import http.client

import logging
logger = logging.getLogger("gs-scroller.urlread")

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
    except (
        http.client.HTTPException,
        urllib.error.URLError,
        IOError, OSError,
    ):
        raise NotResponding
    return reply.read()

