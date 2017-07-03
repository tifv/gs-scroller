from __future__ import division, unicode_literals

from urllib2 import urlopen, HTTPError
from httplib import HTTPException
import re

import lxml.html

from flask import Flask, url_for, abort, render_template

from util import ( Base64Converter, DigitsConverter, DigitListConverter,
    temporary_cache )

app = Flask(__name__)


app.url_map.converters['base64'] = Base64Converter
app.url_map.converters['digits'] = DigitsConverter
app.url_map.converters['digitlist'] = DigitListConverter


@app.route('/')
def default():
    return render_template('default.html')

@app.route('/<base64:sid>/<digits:gid>')
def sheet(sid, gid):
    return convert_google_sheet(sid, gid)

@app.route('/<base64:sid>/')
def spreadsheet(sid):
    title, sheets = google_spreadsheet_data(sid)
    if not sheets:
        raise Google404()
    return render_template('spreadsheet.html', title=title, links=True,
        sid=sid, sheets=sheets, )

@app.route('/<base64:sid>/(<digitlist:gids>)')
def spreadsheet_selection(sid, gids):
    title, sheets = google_spreadsheet_data(sid)
    gids = set(gids)
    sheets = [ sheet
        for sheet in sheets
        if sheet['gid'] in gids ]
    if not sheets:
        raise Google404()
    return render_template('spreadsheet.html', title=title, links=False,
        sid=sid, sheets=sheets, )

@temporary_cache(60*5)
def convert_google_sheet(sid, gid):
    html = parse_google_document(
        'https://docs.google.com/spreadsheets/d/{sid}/pubhtml/sheet?gid={gid}'
        .format(sid=sid, gid=gid) )
    for script in html.iter('script'):
        script.getparent().remove(script)
    html.find('head/link').rewrite_links(
        lambda s: 'https://docs.google.com' + s )
    html.find('head').append(lxml.html.Element( 'link',
        rel='stylesheet', href=url_for('static', filename='metatable.css'),
    ))
    html.find('body').append(lxml.html.Element( 'script',
        src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"
    ))
    html.find('body').append(lxml.html.Element( 'script',
        src=url_for('static', filename='metatable.js')
    ))
    script = lxml.html.Element('script')
    script.text = ( "$(init); "
        "function init() { "
            "$('body').css('overflow', 'hidden'); "
            "var $table = $('#sheets-viewport table').detach(); "
            "var $metatable = create_metatable($table); "
            "$('body').empty().append($metatable); "
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
        .format(sid=sid) )

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
def parse_google_document(url, parser=PARSER):
    try:
        reply = urlopen(url)
    except HTTPError as error:
        if error.code == 404 or error.code == 400:
            raise Google404(url)
        raise
    except HTTPException:
        raise GoogleNotResponding(url)
    if url != reply.geturl():
        print(url, reply.geturl())
        raise Google404(url)
    html_string = reply.read()
    return lxml.html.fromstring(html_string, parser=parser)

class Google404(Exception):
    pass

class GoogleNotResponding(Exception):
    pass

@app.errorhandler(Google404)
def sheet_not_found(exception):
    return render_template('google-404.html'), 404

@app.errorhandler(GoogleNotResponding)
def sheet_timeout(exception):
    return render_template('google-504.html'), 504

@app.errorhandler(404)
def sheet_not_found(exception):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

