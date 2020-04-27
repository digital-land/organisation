#!/usr/bin/env python3

import os
import jinja2
import csv
from collections import OrderedDict
import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from datetime import datetime

from filters.local_authority_type import LocalAuthorityTypeMapping
from utils import get_csv_as_json, joiner

session = CacheControl(requests.session(), cache=FileCache(".cache"))

organisation_csv = os.environ.get("organisation_csv", "https://raw.githubusercontent.com/digital-land/organisation-collection/master/collection/organisation.csv")
organisation_tag_csv = os.environ.get("organisation_tag_csv", "https://raw.githubusercontent.com/digital-land/organisation-collection/master/data/tag.csv")
region_csv = os.environ.get("region_csv", "https://raw.githubusercontent.com/digital-land/organisation-collection/master/data/region.csv")
lrf_csv = os.environ.get("lrf_csv", "https://raw.githubusercontent.com/digital-land/organisation-collection/master/data/lrf.csv")
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


def add_official_names(organisation, datasets):
    for dataset in datasets:
        # index table (dataset[1]) by key (dataset[0])
        master_dict = {x[dataset[0]]: x for x in dataset[1]}
        k_name = dataset[0] + "-name"
        organisation[k_name] = ""
        # add column if identifier present
        if organisation[dataset[0]] != "":
            organisation[k_name] = master_dict.get(organisation[dataset[0]])["name"]
    return organisation


la_type_mapping = LocalAuthorityTypeMapping()
def local_authority_type_filter(k):
    if la_type_mapping.get_local_authority_type_name(k) is not None:
        return la_type_mapping.get_local_authority_type_name(k)
    return k


loader = jinja2.FileSystemLoader(searchpath="./templates")
env = jinja2.Environment(loader=loader)
env.filters["local_authority_type"] = local_authority_type_filter
index_template = env.get_template("index.html")
organisation_template = env.get_template("organisation.html")


# fetch associated data
lrfs = get_csv_as_json(lrf_csv)
regions = get_csv_as_json(region_csv)


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

    # if local authority add region and LRF
    if o["prefix"] == "local-authority-eng":
         add_official_names(o, [('region', regions), ('lrf', lrfs)])

    o.setdefault("tags", [])
    o["tags"].append(prefix)
    tags[prefix]["organisations"].append(o)


for tag in tags:
    for o in tags[tag]["organisations"]:
        o["path"] = "/".join(o["path-segments"])
        render(o["path"] + "/index.html", organisation_template, tags, organisation=o)

with open("docs/index.html", "w") as f:
    f.write(index_template.render(tags=tags, today=today))
