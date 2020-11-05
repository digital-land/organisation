#!/usr/bin/env python3

import os
import jinja2
import json
import csv
from datetime import datetime

import pandas as pd

from utils import joiner
from bin.jinja_setup import setup_jinja

# data endpoints
organisation_csv = os.environ.get("organisation_csv", "https://raw.githubusercontent.com/digital-land/organisation-dataset/master/collection/organisation.csv")
organisation_tag_csv = os.environ.get("organisation_tag_csv", "https://raw.githubusercontent.com/digital-land/organisation-dataset/master/data/tag.csv")
hub_csv = "https://raw.githubusercontent.com/digital-land/organisation-dataset/master/data/hub.csv"
la_to_hub_csv = "https://raw.githubusercontent.com/digital-land/organisation-dataset/master/data/local-authority-to-hub.csv"

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


def render(path, template, data, redirect=False):
    path = os.path.join(docs, path)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, "w") as f:
        f.write(template.render(data=data, today=today, redirect_page=redirect))


def getHubs(data):
    hubs = [x['hub'] for x in data]
    return set(hubs)

def map_las_to_hub(hub, las):
    hub['local-authority'] = [{'name': x['name'], 'informal-name': x['informal-local-authority-name'], 'organisation': x['organisation']} for x in las if x['hub'] == hub['id']]
    hub['lrf'] = list(set([x['lrf-area'] for x in las if x['hub'] == hub['id']]))[0]
    hub['region'] = list(set([x['region'] for x in las if x['hub'] == hub['id']]))[0]
    hub['local-authority'].sort(key=lambda x: x['name'])
    return hub

def map_hub_to_identifier(hub_id, hub_data):
    entries = [x for x in hub_data if x['hub'] == hub_id]
    if len(entries) == 1:
        return {
            'name': entries[0]['name'],
            'informal-name': [entries[0]['informal-name']],
            'organisation': [entries[0]['organisation']]
        }
    else:
        return {
            'name': entries[0]['informal-name'],
            'informal-name': [x['name'] for x in entries],
            'organistion': [x['organisation'] for x in entries]
        }

def mapHubData(hubs, las):
    hubs_ids = getHubs(hubs)
    mapped = {}
    for hub in hubs_ids:
        mapped[hub] = map_hub_to_identifier(hub, hubs)
        mapped[hub]['id'] = hub
        mapped[hub] = map_las_to_hub(mapped[hub], las)
    return mapped


def getHubData():
    data = pd.read_csv(la_to_hub_csv, sep=",")
    las_in_hub_json = json.loads(data.to_json(orient='records'))

    # get hub identifiers
    hub_pd = pd.read_csv(hub_csv, sep=",")
    hub_json = json.loads(hub_pd.to_json(orient='records'))

    # get data from master organisation.csv
    org_pd = pd.read_csv(organisation_csv, sep=",")
    org_data = json.loads(org_pd.to_json(orient='records'))

    # add official names to hub data
    hub_json = joiner(hub_json, org_data, 'organisation', ['name'])
    # add official names to la data
    las_in_hub_json = joiner(las_in_hub_json, org_data, 'organisation', ['name'])

    return mapHubData(hub_json, las_in_hub_json)


# filter for converting local-authority-eng:HCK -> local-authority-eng/HCK
def make_org_url(org_id):
    url_base = '/organisation/'
    if org_id is not None:
        return url_base + org_id.replace(":", "/")
    return org_id


# set up jinja
env = setup_jinja()
env.filters['org_url'] = make_org_url
hub_template = env.get_template("hub.html")

# get hub data augmented with la data
hub_data = getHubData()
# get complete list of org names including informal versions
orgs = set(
    [hub_data[x]['name'] for x in hub_data] +
    [y for x in hub_data for y in hub_data[x]['informal-name']] +
    [y['name'] for x in hub_data for y in hub_data[x]['local-authority']] +
    [y['informal-name'] for x in hub_data for y in hub_data[x]['local-authority']]
)
# sort hub data by region
d = {
    "hubs": sorted(hub_data.items(), key=lambda x: (x[1]['region'], x[0])),
    "councils": sorted(orgs)
}

# we gave out /hub url but now redirect it to /shielding-hub
render("hub.html", hub_template, d, True)
render("shielding-hub.html", hub_template, d, False)
