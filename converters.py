import werkzeug.routing

import logging
logger = logging.getLogger("gs-scroller.converters")

class Base64Converter(werkzeug.routing.BaseConverter):
    regex = r'[0-9a-zA-Z_\-]+'

class DigitsConverter(werkzeug.routing.BaseConverter):
    regex = r'[0-9]+'

class DigitListConverter(werkzeug.routing.BaseConverter):
    regex = '[0-9]+(,[0-9]+)*'
    def to_python(self, value):
        return value.split(',')
    def to_url(self, value):
        return ','.join(value)

