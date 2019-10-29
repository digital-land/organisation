#!/usr/bin/env python3

import os
import jinja2
import csv

loader = jinja2.FileSystemLoader(searchpath="./templates")
env = jinja2.Environment(loader=loader)
index = env.get_template("index.html")

organisations = []
for row in csv.DictReader(open("organisation.csv")):
    organisations.append(row)

with open("index.html", 'w') as f:
    f.write(index.render(organisations=organisations))
