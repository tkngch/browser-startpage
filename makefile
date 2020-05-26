serve:
	.venv/bin/python main.py

build: $(shell find src -type f -name "*.js" -o -name "*.vue")
	npm run build

pyinit:
	python -m venv .venv

pyinstall:
	.venv/bin/pip install -r requirements.txt

python:
	.venv/bin/python

pycheck:
	.venv/bin/mypy api_bookmarks

pyblack:
	.venv/bin/black --check api_bookmarks

pytest:
	.venv/bin/python -m pytest -x -v --pdb --cov=api_bookmarks --cov-report term-missing api_bookmarks

pylint:
	.venv/bin/pylint api_bookmarks
