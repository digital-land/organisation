#!/usr/bin/env python3

from utils import fetch_json_from_endpoint, json_to_csv_file, name_to_identifier


regions_ep = "https://opendata.arcgis.com/datasets/18b9e771acb84451a64d3bcdb3f3145c_0.geojson"


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
