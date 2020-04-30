#!/usr/bin/env python3

def organisation_url_filter(org_id):
    url_base = "/organisation/"
    return url_base + org_id.replace(":", "/")
