#!/usr/bin/env python3

import os
import csv
import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

session = CacheControl(requests.session(), cache=FileCache(".cache"))

local_authority_type_csv = os.environ.get("local_authority_type_csv", "https://raw.githubusercontent.com/digital-land/organisation-dataset/master/collection/register/local-authority-type.csv")

def get(url):
    r = session.get(url)
    r.raise_for_status()
    return r.text

class LocalAuthorityTypeMapping:

    def __init__(self):
        self.local_authority_type_mapping = {}
        for row in csv.DictReader(get(local_authority_type_csv).splitlines()):
            self.local_authority_type_mapping[row['key']] = row['name']
    
    def get_local_authority_type_name(self, local_authority_type):
        return self.local_authority_type_mapping.get(local_authority_type)
