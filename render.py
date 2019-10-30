#!/usr/bin/env python3

import os
import jinja2
import csv

loader = jinja2.FileSystemLoader(searchpath="./templates")
env = jinja2.Environment(loader=loader)
index = env.get_template("index.html")
item = env.get_template("organisation.html")

organisations = []
for o in csv.DictReader(open("organisation.csv")):

    if o["opendatacommunities"]:
        organisations.append(o)

        o["path_segments"] = list(filter(None, o["organisation"].split(":")))
        o["path"] = "/".join(o["path_segments"])

        if o["path"] and not os.path.exists(o["path"]):
            os.makedirs(o["path"])

        with open(o["path"] + "/" + "index.html", "w") as f:
            f.write(item.render(organisation=o))


with open("index.html", "w") as f:
    f.write(index.render(organisations=organisations))
