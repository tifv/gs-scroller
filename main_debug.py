from main import app

import logging

if __name__ == '__main__':
    logging.getLogger("gs-scroller").setLevel(logging.DEBUG)
    app.run(host='127.0.0.1', port=8080, debug=True)

