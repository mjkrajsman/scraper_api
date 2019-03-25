# scrapper_api
Recruitment task

Windows:
set VENV=path\to\venv
python -m venv %VENV%
%VENV%\Scripts\pip install pyramid waitress
%VENV%\Scripts\pip install -e ".[dev]"
%VENV%\Scripts\pytest scrapper_api\tests.py -q
%VENV%\Scripts\pserve development.ini --reload

Linux:
export VENV=~/path/to/venv
python3 -m venv $VENV
$VENV/bin/pip install pyramid waitress
$VENV/bin/pip install -e ".[dev]"
$VENV/bin/pytest scrapper_api/tests.py -q
$VENV/bin/pserve development.ini --reload