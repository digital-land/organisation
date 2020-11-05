#!/usr/bin/env python3

import jinja2

def setup_jinja():
    # register templates
    multi_loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(searchpath=["./templates", "./map-templates"]),
        jinja2.PrefixLoader({
            'govuk-jinja-components': jinja2.PackageLoader('govuk_jinja_components'),
            'digital-land-frontend': jinja2.PackageLoader('digital_land_frontend')
        })
    ])
    env = jinja2.Environment(loader=multi_loader)

    # set variables to make available to all templates
    env.globals["staticPath"] = "https://digital-land.github.io"
    env.globals["urlPath"] = "/design-system"

    return env
