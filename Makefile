.PHONY: init all render clobber black clean prune
.SECONDARY:
.DELETE_ON_ERROR:

all:	render

render:	organisation.csv render.py
	python3 render.py

organisation.csv:
	curl -qs 'https://raw.githubusercontent.com/digital-land/organisation-collection/master/collection/organisation.csv' > $@

black:
	black .

init::
	python3 -m pip install -r requirements.txt

clean:
	rm -rf index.html ./development-corporation/ ./government-organisation/ ./local-authority-eng/ organisation.csv
