#!/usr/bin/env python3

import os
import json
import pandas as pd
from utils import joiner, fetch_json_from_endpoint, json_to_csv_file, name_to_identifier, get_csv_as_json


regions_ep = "https://opendata.arcgis.com/datasets/18b9e771acb84451a64d3bcdb3f3145c_0.geojson"
lrf_ep = "https://opendata.arcgis.com/datasets/d81478eef3904c388091e40f4b344714_0.geojson"
la_to_lrf_ep = "https://opendata.arcgis.com/datasets/203ea94d324b4fcda24875e83e577060_0.geojson"
organisation_csv = os.environ.get("organisation_csv", "https://raw.githubusercontent.com/digital-land/organisation-collection/master/collection/organisation.csv")


def map_region(region):
    props = region['properties']
    return {
        "region": name_to_identifier(props['RGN19NM']),
        "name": props['RGN19NM'],
        "statistical-geography": props['RGN19CD']
    }


def collect_regions():
    print(f"Collect region data from {regions_ep}")
    d = fetch_json_from_endpoint(regions_ep)
    regions = [map_region(r) for r in d['features']]
    return regions


def generate_regions_csv():
    regions = collect_regions()
    regions_csv_path = "data/region.csv"
    print(f'Write region data to {regions_csv_path}')
    json_to_csv_file(regions_csv_path, regions)


def map_lrf(lrf):
    props = lrf['properties']
    return {
        "lrf": name_to_identifier(props['LRF19NM']),
        "name": props['LRF19NM'],
        "statistical-geography": props['LRF19CD']
    }


def collect_lrfs():
    print(f"Collect LRF data from {regions_ep}")
    d = fetch_json_from_endpoint(lrf_ep)
    lrfs = [map_lrf(r) for r in d['features'] if r['properties']['LRF19CD'].startswith('E48')]
    return lrfs


def generate_lrf_csv():
    lrfs = collect_lrfs()
    lrfs_csv_path = "data/lrf.csv"
    print(f'Write LRF data to {lrfs_csv_path}')
    json_to_csv_file(lrfs_csv_path, lrfs)


def collect_la_to_lrf():
    d = fetch_json_from_endpoint(la_to_lrf_ep)
    #return [{'statistical-geography': r['properties']['LAD19CD'], 'lrf': r['properties']['LRF19CD'] } for r in d['features'] if r['properties']['LRF19CD'].startswith('E48')]
    return [{'la-statistical-geography': r['properties']['LAD19CD'], 'lrf-statistical-geography': r['properties']['LRF19CD'] } for r in d['features'] if r['properties']['LRF19CD'].startswith('E48')]


def generate_la_to_lrf_lookup():
    # get data from master organisation.csv
    org_pd = pd.read_csv(organisation_csv, sep=",")
    org_data = json.loads(org_pd.to_json(orient='records'))
    las = [x for x in org_data if x['organisation'].startswith('local-authority-eng:')]

    la_to_lrf = collect_la_to_lrf()
    # firstly join on la statistical geography
    for r in la_to_lrf:
        r['statistical-geography'] = r['la-statistical-geography']
    lookup = joiner(la_to_lrf, las, 'statistical-geography', ['organisation'])

    lrfs = get_csv_as_json("data/lrf.csv")
    # next join on lrf statistical geography
    for r in lookup:
        r['statistical-geography'] = r['lrf-statistical-geography']
    lookup = joiner(lookup, lrfs, 'statistical-geography', ['lrf'])

    # remove temporary 'statistical-geography' key
    for r in lookup:
        r.pop('statistical-geography')

    # write to file
    json_to_csv_file("data/la_to_lrf_lookup.tmp.csv", lookup)
    print("Temporary lookup file created: data/la_to_lrf_lookup.tmp.csv")


# create LRF and Region CSVs
generate_regions_csv()
generate_lrf_csv()
generate_la_to_lrf_lookup()
