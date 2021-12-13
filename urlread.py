import urllib.request
import urllib.error
import http.client

try:
    from google.appengine.api.urlfetch_errors import Error as URLFetchError
except ImportError:
    URLFetchError = None

class HTTPNoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(*args):
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
        print(error.code)
        if error.code in {301, 302, 303, 307, 400, 403, 404, 410}:
            raise NotFound
        raise
    except (
            http.client.HTTPException,
            urllib.error.URLError,
            URLFetchError,
            IOError ):
        raise NotResponding
    return reply.read()

