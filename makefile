.PHONY: serve python pycheck pyblack pytest pylint install clear

SYSTEMD_UNIT_FILE=${HOME}/.config/systemd/user/startpage.service

dist: $(shell find src -type f -name "*.js" -o -name "*.vue")
	npm run build

.venv: requirements.txt
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt

$(SYSTEMD_UNIT_FILE): startpage.service dist .venv
	cp $< $@

install: $(SYSTEMD_UNIT_FILE)

serve: dist .venv
	.venv/bin/python main.py

python: .venv
	.venv/bin/python

pycheck: .venv
	.venv/bin/mypy api_bookmarks

pyblack: .venv
	.venv/bin/black --check api_bookmarks

pytest: .venv
	.venv/bin/python -m pytest -x -v --pdb --cov=api_bookmarks --cov-report term-missing api_bookmarks

pylint: .venv
	.venv/bin/pylint api_bookmarks

clear:
	rm -rf .venv
