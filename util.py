import string
from functools import wraps
import time

import werkzeug.routing

class Base64Converter(werkzeug.routing.BaseConverter):
    regex = '[0-9a-zA-Z_\-]+'

class DigitsConverter(werkzeug.routing.BaseConverter):
    regex = '[0-9]+'

def temporary_cache(timeout):
    def wrapper(function):
        cache = dict()
        def cleanup(current_time):
            old_keys = { key
                for key, (cached_result, cached_time) in cache.items()
                if cached_time < current_time - timeout }
            for key in old_keys:
                del cache[key]
        @wraps(function)
        def wrapped(*args):
            current_time = time.time()
            cached_result, cached_time = cache.get(args, (None, 0))
            delta = current_time - cached_time
            if delta < timeout:
                return cached_result
            result = function(*args)
            cleanup(current_time)
            cache[args] = result, current_time
            return result
        return wrapped
    return wrapper

