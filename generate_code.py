#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Generate Django skeleton code from OpenAPI spec.
"""

import sys

from json import load
from urllib.parse import urlparse
from openapi_utils import Spec, allowed_methods
from generators import DjangoRouteGenerator


def usage():
    ...


def main(scriptname, filepath):
    print(f'Loading the OpenAPI specification in {filepath}')
    with open(filepath, 'r') as fh:
        spec = Spec.create(load(fh))

    generator = DjangoRouteGenerator(spec)
    for pathname in spec.at(['paths']).keys():
        print(generator.view(pathname))


if __name__ == '__main__':
    if sys.argv[1] == '-h':
        usage()
        exit()

    main(*sys.argv)
