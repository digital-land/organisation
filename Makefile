.PHONY: init all render clobber black clean prune
.SECONDARY:
.DELETE_ON_ERROR:

all:	render

render:
	python3 render.py
	python3 render_hub_page.py

black:
	black .

init::
	python3 -m pip install -r requirements.txt

clean:
	rm -rf index.html ./development-corporation/ ./government-organisation/ ./local-authority-eng/ organisation.csv .cache

collect:
	mkdir -p data
	wget -O data/slug-index.csv https://github.com/digital-land/slug-index/raw/main/index/slug-index.csv
