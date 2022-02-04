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

    def __init__(self, timeout, *, max_len=None):
        self.timeout = timeout
        self.cached_times = dict()
        self.time_queue = deque()
        self.max_len = max_len

    def get_cached_value(self, key, generator):
        current_time = time.time()
        old_limit_time = current_time - self.timeout
        cached_time = self.cached_times.get(key)
        if cached_time is not None:
            if cached_time >= old_limit_time:
                cached_result = self.get((key, cached_time), None)
                if cached_result is not None:
                    logger.debug("using cached value")
                    return cached_result[0]
            try:
                del self.cached_times[key]
            except IndexError:
                pass
        self.cleanup_old_cache(old_limit_time)
        return self.set_cached_value(key, current_time, generator())

    def cleanup_old_cache(self, old_limit_time):
        while True:
            if not self.evict_oldest_cache(old_limit_time):
                break

    def evict_oldest_cache(self, old_limit_time=None):
        try:
            (old_key, old_cached_time) = self.time_queue.pop()
        except IndexError:
            return False
        if old_limit_time is not None and old_cached_time > old_limit_time:
            self.time_queue.append((old_key, old_cached_time))
            return False
        try:
            del self[old_key, old_cached_time]
        except IndexError:
            pass
        cached_time = self.cached_times.get(old_key)
        if cached_time is old_cached_time:
            try:
                del self.cached_times[old_key]
            except IndexError:
                pass
        return True

    def set_cached_value(self, key, current_time, value):
        while len(self.time_queue) >= self.max_len:
            if not self.evict_oldest_cache():
                break
        logger.debug("cacheing value")
        self[key, current_time] = (value,)
        self.cached_times[key] = current_time
        self.time_queue.appendleft((key, current_time))
        return value


class MemcacheCache:
    def __init__(self, timeout):
        self.timeout = timeout
    def get_cached_value(self, key, generator):
        logger.debug("getting memcache value")
        cached_result = memcache.get(key)
        if cached_result is not None:
            return cached_result
        result = generator()
        try:
            logger.debug("setting memcache value")
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
        cache = TemporaryCache(timeout, max_len=100)
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
