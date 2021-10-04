#!/usr/bin/env python3

import os
import csv
import json
from collections import OrderedDict
import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from datetime import datetime

from filters.local_authority_type import LocalAuthorityTypeMapping
from filters.organisation_url import organisation_url_filter
from filters.utils import strip_slug, dataset_name
from utils import get_csv_as_json, joiner

from digital_land_frontend.jinja import setup_jinja
from digital_land_frontend.filters import hex_to_rgb_string_filter

session = CacheControl(requests.session(), cache=FileCache(".cache"))

index_csv = os.environ.get("index_csv", "https://github.com/digital-land/slug-index/raw/main/index/slug-index.csv")
organisation_csv = os.environ.get("organisation_csv", "https://raw.githubusercontent.com/digital-land/organisation-dataset/main/collection/organisation.csv")
organisation_tag_csv = os.environ.get("organisation_tag_csv", "https://raw.githubusercontent.com/digital-land/organisation-dataset/main/data/tag.csv")
region_csv = os.environ.get("region_csv", "https://raw.githubusercontent.com/digital-land/region-collection/main/data/region.csv")
lrf_csv = os.environ.get("lrf_csv", "https://raw.githubusercontent.com/digital-land/organisation-dataset/main/data/local-resilience-forum.csv")
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


def constituent_districts(organisations):
    constituent_lists = {}
    combined_authorities = {x['organisation']:x['name'] for x in organisations if x['local-authority-type'] == 'COMB'}
    for comb in combined_authorities.keys():
        constituent_lists.setdefault(comb, {})
        constituent_lists[comb]['name'] = combined_authorities[comb]
        constituent_lists[comb]['organisation'] = comb
        constituent_lists[comb]['constituents'] = [{'organisation':x['organisation'],'name':x['name']} for x in organisations if x['combined-authority'] == comb]
    return constituent_lists


dataset_settings = [
    {
        "dataset": "brownfield-land",
        "label": "Brownfield land",
        "paint_options": {
            "colour": "#745729",
        },
        "type": "point",
    },
    {
        "dataset": "conservation-area",
        "label": "Conservation areas",
        "paint_options": {
            "colour": "#78AA00",
        },
    },
    {
        "dataset": "open-space",
        "label": "Open spaces",
        "paint_options": {
            "colour": "#5694ca",
        },
    }
    ]


def get_referencing_datasets(id):
    url = f'https://datasette.digital-land.info/view_model/geography_datasets_for_organisation.json?organisation={id}'
    data = json.loads(get(url))
    datasetNames = [d[0] for d in data['rows']]
    return [d for d in dataset_settings if d['dataset'] in datasetNames]

la_type_mapping = LocalAuthorityTypeMapping()
def local_authority_type_filter(k):
    if la_type_mapping.get_local_authority_type_name(k) is not None:
        return la_type_mapping.get_local_authority_type_name(k)
    return k

# set up jinja
env = setup_jinja()
# register filters
env.filters["local_authority_type"] = local_authority_type_filter
env.filters["organisation_url"] = organisation_url_filter
env.filters["clean_slug"] = strip_slug
env.filters["clean_dataset_name"] = dataset_name
env.filters["hex_to_rgb"] = hex_to_rgb_string_filter
# get page templates
index_template = env.get_template("index.html")
organisation_template = env.get_template("organisation.html")
organisation_map_template = env.get_template("organisation-map.html")


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

    # if local authority add region and local resilience forum
    if o["prefix"] == "local-authority-eng":
         add_official_names(o, [('region', regions), ('local-resilience-forum', lrfs)])

    o.setdefault("tags", [])
    o["tags"].append(prefix)
    tags[prefix]["organisations"].append(o)

combined_authority_lists = constituent_districts(tags['local-authority-eng']["organisations"])

from collections import defaultdict
index = defaultdict(dict)

# build children dict
for child in csv.DictReader(get(index_csv).splitlines()):
    i = index[child["organisation"]]
    i.setdefault(child["dataset"], [])
    i[child["dataset"]].append(child)

for tag in tags:
    for o in tags[tag]["organisations"]:
        o["path"] = "/".join(o["path-segments"])
        if tag == 'local-authority-eng':
            if o.get('local-authority-type') == 'COMB':
                o['constituent-districts'] = combined_authority_lists[o['organisation']]['constituents']
            if o['combined-authority']:
                comb_id = o['combined-authority']
                o['combined-authority'] = {
                    'organisation': comb_id,
                    'name': combined_authority_lists[comb_id]['name']
                }

        o["children"] = {}
        if o["organisation"] in index:
            o["children"] = index[o["organisation"]]
        
        # render a planning-data for local authorities
        if 'local-authority-eng' in o['tags']:
            o['dataset_settings'] = get_referencing_datasets(o['organisation'])
            o['datasets'] = [
                { 'name': 'local-authority-district', 'type': 'shape' }
            ]
            for d in o['dataset_settings']:
                da = {
                    'name': d['dataset']
                }
                da['type'] = d['type'] if 'type' in d.keys() else 'shape'
                o['datasets'].append(da)
            render(o["path"] + "/planning-data" + "/index.html", organisation_map_template, tags, organisation=o)

        render(o["path"] + "/index.html", organisation_template, tags, organisation=o)

with open("docs/index.html", "w") as f:
    f.write(index_template.render(tags=tags, today=today))
