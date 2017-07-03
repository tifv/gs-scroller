# gs-scroller
A simple HTTP server allowing embedding Google Spreadsheets with scrolling and frozen rows/columns.

# Installation
Provided that you are in [Google Cloud Shell](https://console.cloud.google.com/cloudshell)
and target project is already selected, this should deploy the app to the project:

    $ git clone https://github.com/tifv/gs-scroller.git
    $ cd gs-scroller
    $ pip install -r requirements.txt -t lib/
    $ gcloud app deploy

(Of course, you can do the same from your computer if you have necessary tools.)
