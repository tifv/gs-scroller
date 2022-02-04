import re

import lxml.html

from flask import Flask, url_for, abort, render_template

import logging
logger = logging.getLogger("gs-scroller.main")

if __name__ == '__main__':
    logging.getLogger("gs-scroller").setLevel(logging.INFO)
else:
    logging.getLogger("gs-scroller").setLevel(logging.INFO)
    try:
        import google.cloud.logging
        logging_client = google.cloud.logging.Client()
        from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging
        logging_handler = CloudLoggingHandler(logging_client)
    except ImportError:
        logger.warning("Google's logging module could not be imported")
    else:
        setup_logging(logging_handler)
        logger.info("Google's logging module was imported")
        logger.debug("Debug messages will be logged")

try:
    from google.appengine.api import wrap_wsgi_app
except ImportError:
    logger.warning("Google's appengine wrapper could not be imported")
    wrap_wsgi_app = None
else:
    logger.info("Google's appengine wrapper was imported")

from converters import (
    Base64Converter, DigitsConverter, DigitListConverter )
from cache import temporary_cache
import urlread

GOOGLE_TIMEOUT=30

app = Flask(__name__)
if wrap_wsgi_app is not None:
    app.wsgi_app = wrap_wsgi_app(app.wsgi_app)

app.url_map.converters['base64'] = Base64Converter
app.url_map.converters['digits'] = DigitsConverter
app.url_map.converters['digitlist'] = DigitListConverter


@app.route('/')
def default():
    return render_template('default.html')

@app.route('/e/<base64:sid>/<digits:gid>')
def sheet_e(sid, gid):
    return sheet(sid="e/"+sid, gid=gid)

@app.route('/<base64:sid>/<digits:gid>')
def sheet(sid, gid):
    return convert_google_sheet(sid, gid)

@app.route('/e/<base64:sid>/')
def spreadsheet_e(sid):
    return spreadsheet(sid="e/"+sid)

@app.route('/<base64:sid>/')
def spreadsheet(sid):
    title, sheets = google_spreadsheet_data(sid)
    if not sheets:
        raise GoogleSpreadsheetNotFound()
    return render_template('spreadsheet.html', title=title, links=True,
        sid=sid, sheets=sheets, )

@app.route('/e/<base64:sid>/(<digitlist:gids>)')
def spreadsheet_selection_e(sid, gids):
    return spreadsheet_selection(sid="e/"+sid, gids=gids)

@app.route('/<base64:sid>/(<digitlist:gids>)')
def spreadsheet_selection(sid, gids):
    try:
        title, sheets = google_spreadsheet_data(sid)
    except GoogleSpreadsheetNotResponding as error:
        error.sid = error.gid = None
        raise
    gids = set(gids)
    sheets = [ sheet
        for sheet in sheets
        if sheet['gid'] in gids ]
    if not sheets:
        raise GoogleSpreadsheetNotFound()
    return render_template('spreadsheet.html', title=title, links=False,
        sid=sid, sheets=sheets, )

@temporary_cache(60*5)
def convert_google_sheet(sid, gid):
    html = parse_google_document(
        'https://docs.google.com/spreadsheets/d/{sid}/pubhtml/sheet?gid={gid}'
            .format(sid=sid, gid=gid),
        errhelp={'sid' : sid, 'gid' : gid} )
    for script in html.iter('script'):
        script.getparent().remove(script)
    for link in html.find('head').iter('link'):
        link.rewrite_links(
            lambda s:
                'https:' + s
                    if s.startswith('//') else
                'https://docs.google.com' + s )
    html.find('head').append(lxml.html.Element( 'link',
        rel='stylesheet', href=url_for('static', filename='metatable.css'),
    ))
    html.find('body').append(lxml.html.Element( 'script',
        src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"
    ))
    html.find('body').append(lxml.html.Element( 'script',
        src=url_for('static', filename='metatable.js')
    ))
    script = lxml.html.Element('script')
    script.text = ( "$(init); "
        "function init() { "
            "$('body').css('overflow', 'hidden'); "
            "var $viewport = $('#sheets-viewport').detach(); "
            "var $table = $viewport.find('table').detach(); "
            "var $svgs = $viewport.find('svg'); "
            "var $metatable = create_metatable($table); "
            "$('body').empty(); "
            "$('body').append($svgs); "
            "$('body').append($metatable); "
            "$viewport.remove(); "
            "$metatable.resize(); "
        " }" )
    html.find('body').append(script)
    return b'<!DOCTYPE html>\n<meta charset="UTF-8">\n' + \
        lxml.html.tostring(html, encoding='utf-8')

SHEET_PATTERN = re.compile(
    r'{[^{}]*'
        r'name: "(?P<name>[^"]+)"'
    r'[^{}]*'
        r'gid: "(?P<gid>\d+)"'
    r'[^{}]*}' )
@temporary_cache(60*5)
def google_spreadsheet_data(sid):
    html = parse_google_document(
        'https://docs.google.com/spreadsheets/d/{sid}/pubhtml?widget=true'
            .format(sid=sid),
        errhelp={'sid' : sid} )

    title = html.find('head/title').text
    sheets = []
    for script in html.iter('script'):
        if script.text is None:
            continue
        for match in SHEET_PATTERN.finditer(script.text):
            sheets.append(match.groupdict())
        if sheets:
            break
    return title, sheets

PARSER = lxml.html.HTMLParser(encoding="utf-8")
def parse_google_document(url, errhelp=None, parser=PARSER):
    try:
        reply_text = urlread.urlread(url, timeout=GOOGLE_TIMEOUT)
    except urlread.NotFound:
        raise GoogleSpreadsheetNotFound(errhelp)
    except urlread.NotResponding:
        raise GoogleSpreadsheetNotResponding(errhelp)
    return lxml.html.fromstring(reply_text, parser=parser)

class GoogleSpreadsheetException(Exception):
    def __init__(self, errhelp=None):
        super(GoogleSpreadsheetException, self).__init__(self)
        if errhelp is not None:
            self.sid = errhelp.get('sid')
            self.gid = errhelp.get('gid')
        else:
            self.sid = self.gid = None

class GoogleSpreadsheetNotFound(GoogleSpreadsheetException):
    pass

class GoogleSpreadsheetNotResponding(GoogleSpreadsheetException):
    pass

@app.errorhandler(GoogleSpreadsheetNotFound)
def sheet_not_found(exception):
    return render_template('google-404.html', sid=exception.sid, gid=exception.gid), 404

@app.errorhandler(GoogleSpreadsheetNotResponding)
def sheet_timeout(exception):
    return render_template('google-504.html', sid=exception.sid, gid=exception.gid), 504

@app.errorhandler(404)
def not_found(exception):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

