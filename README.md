# gs-scroller
An HTTP server returning embeddable version of published Google spreadsheets—with frozen rows and columns.

# Testing
Install `lxml` and `Flask` Python modules. After that,

    $ git clone https://github.com/tifv/gs-scroller.git
    $ cd gs-scroller
    $ python3 main.py

Use `main_debug.py` instead of `main.py` to get various debugging features of Flask.

# Installation
Provided that you are in the [Google Cloud Shell](https://console.cloud.google.com/cloudshell)
and a target project is already selected (like with `gcloud config set project project_name`), this should deploy the app to the project:

    $ git clone https://github.com/tifv/gs-scroller.git
    $ cd gs-scroller
    $ gcloud app deploy

(Of course, you can do the same from your computer if you have the necessary tools.)
