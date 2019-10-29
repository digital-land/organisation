all:	render

render:	organisation.csv render.py
	python3 render.py

organisation.csv:
	curl -qs 'https://raw.githubusercontent.com/digital-land/organisation-collection/master/collection/organisation.csv' > $@

init::
	python3 -m pip install -r requirements.txt
