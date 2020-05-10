serve:
	python main.py

test:
	python -m pytest -x -v --pdb --cov=api_bookmarks --cov-report term-missing api_bookmarks

build: $(shell find src -type f -name "*.js" -o -name "*.vue")
	npm run build
