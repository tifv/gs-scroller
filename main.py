# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]

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
    except urllib.error.HTTPError:
        abort(404)
    for script in html.iter('script'):
        script.getparent().remove(script)
    html.find('head/link').rewrite_links(lambda s: 'https://docs.google.com' + s)
    html.find('body').append(lxml.html.Element(
        'script', src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"
    ))
    html.find('body').append(lxml.html.Element(
        'script', src=url_for('static', filename='convert.js')
    ))
    script = lxml.html.Element('script')
    script.text = ( "$(init); "
        "function init() { "
            "$('body').css('overflow', 'hidden'); "
            "split_and_rock( $('#sheets-viewport table'));"
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
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

# [END app]
