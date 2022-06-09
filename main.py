#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests

from json import load
from urllib.parse import urlparse
from openapi_core import create_spec
from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.contrib.requests import RequestsOpenAPIResponse
from openapi_core.validation.response.validators import ResponseValidator


def usage():
    usage_string = """
Usage:
$ apitester -h
Prints this help text.
$ apitester filepath [server]
Validates the API specified in the OpenAPI document at the given `filepath`.
`filepath`  local path to the OpenAPI specification
`server`    index of the server objects to test. If none is given, all servers will be checked. 
    """
    print(usage_string)
    exit(0)


allowed_methods = ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH', 'TRACE']


def main(scriptname, filepath):
    print(f'Loading the OpenAPI specification in {filepath}')
    with open(filepath, 'r') as fh:
        spec = create_spec(load(fh))
    validator = ResponseValidator(spec)

    base_path = spec.accessor.dopen(['servers', 0, 'url'])
    print(base_path)

    with spec.accessor.open(['paths']) as paths:
        for patterned_path in paths.keys():
            path = patterned_path
            for method, operation in spec.accessor.dopen(['paths', patterned_path]).items():
                if not method.upper() in allowed_methods:
                    continue
                # resolve path with example data
                if "{" in path:
                    for i in range(len(spec.accessor.dopen(['paths', patterned_path, 'parameters']))):
                        parameter = spec.accessor.dopen(['paths', patterned_path, 'parameters', i])
                        if not ('example' in parameter.keys() or 'examples' in parameter.keys()):
                            raise KeyError(f"Parameter {parameter['name']} does not define examples.")
                        path = path.replace("{" + parameter['name'] + "}", str(parameter['example']))

                url = urlparse(base_path)
                url = url._replace(path=url.path + path)
                # print(method, url.path)
                # TODO: Add example headers to the request
                request = requests.Request(method, url.geturl())
                prepared = request.prepare()
                with requests.Session() as s:
                    s.verify = False
                    response = s.send(prepared)
                    # print(response.status_code, response.reason)
                    result = validator.validate(RequestsOpenAPIRequest(request), RequestsOpenAPIResponse(response))
                    if len(result.errors) > 0:
                        print(repr(result.errors))
                        if response.content:
                            print(response.content)


if __name__ == '__main__':
    if sys.argv[1] == '-h':
        usage()

    main(*sys.argv)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
