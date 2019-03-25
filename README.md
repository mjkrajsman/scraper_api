# scraper_api
Recruitment task

1. Windows:
* `set VENV=path\to\venv`
* `python -m venv %VENV%`
* `%VENV%\Scripts\pip install pyramid waitress`
* `%VENV%\Scripts\pip install -e ".[dev]"`
* `%VENV%\Scripts\initialize_db development.ini`
* `%VENV%\Scripts\pytest scraper_api\tests.py -q`
* `%VENV%\Scripts\pserve development.ini --reload`

2. Linux:
* `export VENV=~/path/to/venv`
* `python3 -m venv $VENV`
* `$VENV/bin/pip install pyramid waitress`
* `$VENV/bin/pip install -e ".[dev]"`
* `$VENV/bin/initialize_db development.ini`
* `$VENV/bin/pytest scraper_api/tests.py -q`
* `$VENV/bin/pserve development.ini --reload`
