#!/usr/bin/env python3

import os
import json
import csv
import requests

import pandas as pd


def get_csv_as_json(path_to_csv):
    csv_pd = pd.read_csv(path_to_csv, sep=",")
    return json.loads(csv_pd .to_json(orient='records'))


# write json to csv file
def json_to_csv_file(output_file, data):
    # now we will open a file for writing 
    data_file = open(output_file, 'w')
    # create the csv writer object 
    csv_writer = csv.writer(data_file)
    # Counter variable used for writing  
    # headers to the CSV file
    count = 0

    for row in data: 
        if count == 0: 
    
            # Writing headers of CSV file 
            header = row.keys() 
            csv_writer.writerow(header) 
            count += 1
    
        # Writing data of CSV file 
        csv_writer.writerow(row.values()) 
    
    data_file.close()


def join_col(d1, idx_d2, k, col):
    for row in d1:
        if row[k] is not None:
            #print("Record: ", idx_d2[row[k]])
            if idx_d2.get(row[k]) is not None:
                row[col] = idx_d2[row[k]][col]
            else:
                print(f"no match for '{k}'", row[k])
                row[col] = None
            #print(row)
    return d1


def joiner(d1, d2, k, cols):
    if k in d1[0].keys() and k in d2[0].keys():
        # need to check for potential column clashes

        # index d2 by key
        d2_idx = {x[k]: x for x in d2}

        for col in cols:
            if col in d2[0].keys():
                d1 = join_col(d1, d2_idx, k, col)
    return d1


def fetch_json_from_endpoint(endpoint):
    json_url = requests.get(endpoint)
    return json_url.json()


def name_to_identifier(n):
    return n.lower().replace(" ", "-").replace(",", "")


# test by calling something like 
def testjoiner(cols):
    d1 = pd.read_csv("./data/hubs.csv", sep=",")
    jd1 = json.loads(d1.to_json(orient='records'))

    # organisation_csv = os.environ.get("organisation_csv", "https://raw.githubusercontent.com/digital-land/organisation-dataset/main/collection/organisation.csv")
    # d2 = pd.read_csv(organisation_csv, sep=",")
    # jd2 = json.loads(d2.to_json(orient='records'))
    d2 = pd.read_csv("./data/hubsv2.csv", sep=",")
    jd2 = json.loads(d2.to_json(orient='records'))

    new_data = joiner(jd1, jd2, 'informal-name', cols)
    # print sample record
    print(new_data[3])

    # save to csv
    # json_to_csv_file('data/rishi_data.csv', new_data)
