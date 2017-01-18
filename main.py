import string

#import urllib.request as urlrequest
import urllib2 as urlrequest

import logging

try:
    import lxml.etree
    import lxml.html
except ImportError:
    logging.fatal("lxml not loaded")
    raise

try:
    from flask import Flask, url_for, abort, render_template
except ImportError:
    logging.fatal("flask not loaded")
    raise


app = Flask(__name__)


@app.route('/')
def default():
    return render_template('default.html')

BASE64_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase + "_-"

@app.route('/<sid>/<gid>')
def sheet(sid, gid):
    if not all(s in BASE64_ALPHABET for s in sid):
        raise ValueError("Spreadsheet ID must be wrong")
    if not gid.isdigit():
        raise ValueError("Sheet ID (gid) must be wrong")
    docs_href = ( 'https://docs.google.com/spreadsheets/d/{sid}/pubhtml/sheet?gid={gid}'
        .format(sid=sid, gid=gid) )
    parser = lxml.html.HTMLParser(encoding="utf-8")
    try:
        html = lxml.html.fromstring(urlrequest.urlopen(docs_href).read(),
            parser=parser )
    except urlrequest.HTTPError:
        abort(404)
    for script in html.iter('script'):
        script.getparent().remove(script)
    html.find('head/link').rewrite_links(lambda s: 'https://docs.google.com' + s)
    html.find('head').append(lxml.html.Element(
        'link', rel='stylesheet', href=url_for('static', filename='metatable.css'),
    ))
    html.find('body').append(lxml.html.Element(
        'script', src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"
    ))
    html.find('body').append(lxml.html.Element(
        'script', src=url_for('static', filename='metatable.js')
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
    return b'<!DOCTYPE html><meta charset="UTF-8">' + lxml.html.tostring(html)

#@app.errorhandler(500)
#def server_error(e):
#    logging.exception('An error occurred during a request.')
#    return """
#    An internal error occurred: <pre>{}</pre>
#    See logs for full stacktrace.
#    """.format(e), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

