#!/usr/bin/env python3

import os
import jinja2
import csv
from collections import OrderedDict
from datetime import datetime


def date_text(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%-d %B %Y")
    except ValueError:
        return None


loader = jinja2.FileSystemLoader(searchpath="./templates")
env = jinja2.Environment(loader=loader)
index = env.get_template("index.html")
item = env.get_template("organisation.html")

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
        o["path"] = "docs/" + "/".join(o["path-segments"])

        if o["path"] and not os.path.exists(o["path"]):
            os.makedirs(o["path"])

        with open(o["path"] + "/" + "index.html", "w") as f:
            f.write(item.render(organisation=o))

with open("docs/index.html", "w") as f:
    f.write(index.render(tags=tags))
