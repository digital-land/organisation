.PHONY: init all render clobber black clean prune
.SECONDARY:
.DELETE_ON_ERROR:

all:	render

render:
	python3 render.py
	python3 render_hub_page.py

black:
	black .
	
submodules::
	git submodule update --init --remote
	git pull --recurse-submodules

init:: submodules
	python3 -m pip install -r requirements.txt

clean:
	rm -rf index.html ./development-corporation/ ./government-organisation/ ./local-authority-eng/ organisation.csv .cache
