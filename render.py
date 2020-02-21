#!/usr/bin/env python3

import os
import jinja2
import csv
from collections import OrderedDict
import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from datetime import datetime

session = CacheControl(requests.session(), cache=FileCache(".cache"))

organisation_csv = os.environ.get("organisation_csv", "https://raw.githubusercontent.com/digital-land/organisation-collection/master/collection/organisation.csv")
organisation_tag_csv = os.environ.get("organisation_tag_csv", "https://raw.githubusercontent.com/digital-land/organisation-collection/master/data/tag.csv")
docs = "docs/"
today = datetime.utcnow().isoformat()[:10]


def get(url):
    r = session.get(url)
    r.raise_for_status()
    return r.text



def date_text(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%-d %B %Y")
    except ValueError:
        return None


def render(path, template, tags, organisation=None):
    path = os.path.join(docs, path)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, "w") as f:
        f.write(template.render(tags=tags, organisation=organisation, today=today))


loader = jinja2.FileSystemLoader(searchpath="./templates")
env = jinja2.Environment(loader=loader)
index_template = env.get_template("index.html")
organisation_template = env.get_template("organisation.html")

tags = OrderedDict()
for o in csv.DictReader(get(organisation_tag_csv).splitlines()):
    o["organisations"] = []
    tags[o["tag"]] = o


for o in csv.DictReader(get(organisation_csv).splitlines()):
    o["path-segments"] = list(filter(None, o["organisation"].split(":")))
    prefix = o["prefix"] = o["path-segments"][0]
    o["id"] = o["path-segments"][1]

    o["start-date-text"] = date_text(o["start-date"])
    o["end-date-text"] = date_text(o["end-date"])

    o.setdefault("tags", [])
    o["tags"].append(prefix)
    tags[prefix]["organisations"].append(o)


for tag in tags:
    for o in tags[tag]["organisations"]:
        o["path"] = "/".join(o["path-segments"])
        render(o["path"] + "/index.html", organisation_template, tags, organisation=o)

with open("docs/index.html", "w") as f:
    f.write(index_template.render(tags=tags))
