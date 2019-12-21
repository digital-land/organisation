#!/usr/bin/env python3

import os
import jinja2
import csv
from collections import OrderedDict
from datetime import datetime

docs = "docs/"

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
        f.write(template.render(tags=tags, organisation=organisation))


loader = jinja2.FileSystemLoader(searchpath="./templates")
env = jinja2.Environment(loader=loader)
index_template = env.get_template("index.html")
organisation_template = env.get_template("organisation.html")

tags = OrderedDict()
for o in csv.DictReader(open("tag.csv")):
    o["organisations"] = []
    tags[o["tag"]] = o


for o in csv.DictReader(open("organisation.csv")):
    o["path-segments"] = list(filter(None, o["organisation"].split(":")))
    prefix = o["prefix"] = o["path-segments"][0]
    o["id"] = o["path-segments"][1]

    o["start-date-text"] = date_text(o["start-date"])
    o["end-date-text"] = date_text(o["end-date"])

    o.setdefault("tags", [])
    o["tags"].append(prefix)

    if (prefix in tags) and (
        o["opendatacommunities"]
        or o["wikidata"]
        or o["path-segments"][0] in ("local-authority-eng", "development-corporation")
    ):
        tags[prefix]["organisations"].append(o)


for tag in tags:
    for o in tags[tag]["organisations"]:
        o["path"] = "/".join(o["path-segments"])
        render(o["path"] + "/index.html", organisation_template, tags, organisation=o)

with open("docs/index.html", "w") as f:
    f.write(index_template.render(tags=tags))
