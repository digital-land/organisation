#!/usr/bin/env python3

import os
import jinja2
import json
import csv
from datetime import datetime

import pandas as pd


organisation_csv = os.environ.get("organisation_csv", "https://raw.githubusercontent.com/digital-land/organisation-collection/master/collection/organisation.csv")
organisation_tag_csv = os.environ.get("organisation_tag_csv", "https://raw.githubusercontent.com/digital-land/organisation-collection/master/data/tag.csv")
hub_csv = "https://raw.githubusercontent.com/digital-land/organisation-collection/master/data/hub.csv"
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


def render(path, template, data):
    path = os.path.join(docs, path)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, "w") as f:
        f.write(template.render(data=data, today=today))


def getHubs(data):
    hubs = [x['informal-hub-name'] for x in data]
    return set(hubs)

def mapAHub(hub, data):
    return {
        'local-authority': [(x['local-authority-name'], x['organisation']) for x in data if x['informal-hub-name'] == hub],
        'lrf': list(set([x['lrf-area'] for x in data if x['informal-hub-name'] == hub]))[0],
        'region': list(set([x['region'] for x in data if x['informal-hub-name'] == hub]))[0],
        'id': list(set([x['hub'] for x in data if x['informal-hub-name'] == hub]))[0]
    }

def mapHubData(data):
    hubs = getHubs(data)
    mapped = {}
    for hub in hubs:
        mapped[hub] = mapAHub(hub, data)
    return mapped


def getHubData():
    data = pd.read_csv("./data/las_in_hubs.csv", sep=",")
    json_data = json.loads(data.to_json(orient='records'))
    councils = [x['local-authority-name'] for x in json_data]

    # get hub identifiers
    hId = pd.read_csv("./data/hubs.v2.csv", sep=",")
    jhId = json.loads(hId.to_json(orient='records'))

    # combine local authorities and hubs
    orgs = list(set([x['informal-name'] for x in jhId] + councils))

    return orgs, mapHubData(json_data)


# filter for converting local-authority-eng:HCK -> local-authority-eng/HCK
def make_org_url(org_id):
    url_base = '/organisation/'
    if org_id is not None:
        return url_base + org_id.replace(":", "/")
    return org_id


loader = jinja2.FileSystemLoader(searchpath="./templates")
env = jinja2.Environment(loader=loader)
env.filters['org_url'] = make_org_url
hub_template = env.get_template("hub.html")


# sort hub data by region
councils, data = getHubData()
d = {
    "hubs": sorted(data.items(), key=lambda x: (x[1]['region'], x[0])),
    "councils": sorted(councils)
}

render("hub.html", hub_template, d)
