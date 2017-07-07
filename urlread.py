import urllib2
import httplib

try:
    from google.appengine.api.urlfetch_errors import Error as URLFetchError
except ImportError:
    URLFetchError = None

class HTTPNoRedirectHandler(urllib2.HTTPRedirectHandler):
    def redirect_request(*args):
        return None

urllib2.install_opener(urllib2.build_opener(HTTPNoRedirectHandler))

class NotFound(Exception):
    pass

class NotResponding(Exception):
    pass

def urlread(url, timeout=30):
    try:
        reply = urllib2.urlopen(url, timeout=timeout)
    except urllib2.HTTPError as error:
        if error.code in {301, 302, 303, 307, 400, 404}:
            raise NotFound
        raise
    except (httplib.HTTPException, urllib2.URLError, URLFetchError, IOError):
        raise NotResponding
    return reply.read()

