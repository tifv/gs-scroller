import string
from functools import wraps, partial
from collections import deque
import time

import logging
logger = logging.getLogger("gs-scroller.cache")

# try:
#     from google.appengine.api import memcache
# except ImportError:
#     logger.warning("Google's memcache module could not be imported")
#     memcache = None
# else:
#     logger.info("Google's memcache module was imported")
memcache = None

class TemporaryCache(dict):
    def __init__(self, timeout, *, maxlen=None):
        self.timeout = timeout
        self.time_queue = deque(maxlen=maxlen)
    def get_cached_value(self, key, generator):
        current_time = time.time()
        cache_limit_time = current_time - self.timeout
        cached_result, cached_time = self.get(key, (None, 0))
        if cached_time >= cache_limit_time:
            return cached_result
        while self.time_queue and self.time_queue[-1][1] < cache_limit_time:
            del self[self.time_queue.pop()[0]]
        result = generator()
        self[key] = result, current_time
        self.time_queue.appendleft((key, current_time))
        return result

class MemcacheCache:
    def __init__(self, timeout):
        self.timeout = timeout
    def get_cached_value(self, key, generator):
        logger.debug("getting memcache key")
        cached_result = memcache.get(key)
        if cached_result is not None:
            return cached_result
        result = generator()
        try:
            logger.debug("setting memcache key")
            memcache.add(key, result, self.timeout)
        except ValueError:
            logger.info("error while setting memcache key", exc_info=True)
            pass
        return result

def temporary_cache(timeout):
    """
    Decorator. Implement cacheing of function results.

    Function arguments must always be strings, and never contain slash.
    """
    if memcache is None:
        cache = TemporaryCache(timeout, maxlen=100)
    else:
        cache = MemcacheCache(timeout)
    def wrapper(function, timeout=timeout, cache=cache):
        @wraps(function)
        def wrapped(*args):
            generator = partial(function, *args)
            key = '/'.join(args)
            return cache.get_cached_value(key, generator)
        return wrapped
    return wrapper
