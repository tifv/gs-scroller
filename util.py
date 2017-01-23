import string
from functools import wraps
import time

import werkzeug.routing

class Base64Converter(werkzeug.routing.BaseConverter):
    regex = '[0-9a-zA-Z_\-]+'

class DigitsConverter(werkzeug.routing.BaseConverter):
    regex = '[0-9]+'

class TemporaryError(Exception):
    pass

def temporary_cache(timeout_min, timeout_max):
    def wrapper(function):
        cache = dict()
        def cleanup(current_time):
            old_keys = { key
                for key, (cached_result, cached_time) in cache.items()
                if cached_time < current_time - timeout_max }
            for key in old_keys:
                del cache[key]
        @wraps(function)
        def wrapped(*args):
            current_time = time.time()
            cached_result, cached_time = cache.get(args, (None, 0))
            delta = current_time - cached_time
            if delta < timeout_min:
                return cached_result
            try:
                result = function(*args)
            except TemporaryError as error:
                if delta < timeout_max:
                    return cached_result
                else:
                    raise
            else:
                cleanup(current_time)
                cache[args] = result, current_time
                return result
        return wrapped
    return wrapper

