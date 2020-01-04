.PHONY: init all render clobber black clean prune
.SECONDARY:
.DELETE_ON_ERROR:

all:	render

render:
	python3 render.py

black:
	black .

init::
	python3 -m pip install -r requirements.txt

clean:
	rm -rf index.html ./development-corporation/ ./government-organisation/ ./local-authority-eng/ organisation.csv
