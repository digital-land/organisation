#!/usr/bin/env python3

import os
import jinja2
import csv
from collections import OrderedDict
import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from datetime import datetime

from utils import get_csv_as_json, joiner

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


def add_to_org_from_lookup(record, lookup, master, k, col):
    # set identifier if exists in lookup
    record[k] = lookup.get(record['organisation'], "")
    # index master table by key
    master_dict = {x[k]: x for x in master}
    col_key = k + "-" + col
    record[col_key] = ""
    # add column if lookup entry existed
    if record[k] != "":
        record[col_key] = master_dict.get(record[k])[col]
    return o


# fetch LA to LRF lookup table
la_to_lrf_lookup = get_csv_as_json("data/la_to_lrf_lookup.csv")
la_to_lrf_lookup_dict = {x['organisation']:x['lrf'] for x in la_to_lrf_lookup}
# fetch lrf master table
lrfs = get_csv_as_json("data/lrf.csv")
def add_lrf(o):
    return add_to_org_from_lookup(o, la_to_lrf_lookup_dict, lrfs, 'lrf', 'name')


# fetch LA to Region lookup table
la_to_region_lookup = get_csv_as_json("data/la_to_region_lookup.csv")
la_to_region_lookup_dict = {x['organisation']:x['region'] for x in la_to_region_lookup}
# fetch region csv
regions = get_csv_as_json("data/region.csv")
def add_region(o):
    return add_to_org_from_lookup(o, la_to_region_lookup_dict, regions, 'region', 'name')


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
        # if local authority add LRF
        if tag == "local-authority-eng":
            o = add_lrf(o)
            o = add_region(o)
        render(o["path"] + "/index.html", organisation_template, tags, organisation=o)

with open("docs/index.html", "w") as f:
    f.write(index_template.render(tags=tags))
