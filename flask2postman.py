#!/usr/bin/env python
from __future__ import print_function

import re
import sys
from copy import copy
from time import time
from uuid import uuid4

__version__ = "1.0.8"

methods_order = ["GET", "POST", "PUT", "PATCH", "DELETE", "COPY", "HEAD",
                 "OPTIONS", "LINK", "UNLINK", "PURGE"]

var_re = re.compile(r"(?P<var><[a-zA-Z0-9_]+:(?P<var_name>[a-zA-Z0-9_]+)>)")

venv_warning = ("WARNING: Attempting to work in a virtualenv. If you encounter "
                "problems, please install flask2postman inside the virtualenv.")


def get_time():
    return int(round(time() * 1000))


class Collection:

    def __init__(self, name):
        self.id = str(uuid4())
        self._requests = []
        self.name = name
        self.timestamp = get_time()

    def reorder_requests(self):
        def _get_key(request):
            return str(methods_order.index(request.method)) + request.name
        self._requests = sorted(self._requests, key=_get_key)

    def add_route(self, route):
        route.collection_id = self.id
        self._requests.append(route)
        self.reorder_requests()

    @property
    def order(self):
        return [request.id for request in self._requests]

    @property
    def requests(self):
        return [request.to_dict() for request in self._requests]

    def to_dict(self):
        d = copy(self.__dict__)
        d.pop("_requests")
        d.update(requests=self.requests, order=self.order)
        return d


class Route:

    def __init__(self, name, url, method, description="", headers="", data=[],
                 data_mode="params"):
        self.id = str(uuid4())
        self.data = data
        self.data_mode = data_mode
        self.description = description
        self.headers = headers
        self.method = method
        self.name = name
        self.time = get_time()
        self.url = url

    def to_dict(self):
        d = copy(self.__dict__)
        d["collectionId"] = d.pop("collection_id")
        d["dataMode"] = d.pop("data_mode")
        return d

    @classmethod
    def from_werkzeug(cls, rule, method, base_url):
        name = rule.endpoint.rsplit('.', 1)[-1]
        name = name.split("_", 1)[-1]
        name = name.replace("_", " ")

        url = base_url + rule.rule
        for match in re.finditer(var_re, url):
            var = match.group("var")
            var_name = "{{" + match.group("var_name") + "}}"
            url = url.replace(var, var_name)
        return cls(name, url, method)


# ramnes: shamelessly stolen from https://www.python.org/dev/peps/pep-0257/
def trim(docstring):
    if not docstring:
        return ""
    lines = docstring.expandtabs().splitlines()
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    return '\n'.join(trimmed)


def main():
    import json
    import logging
    import os
    import site
    from argparse import ArgumentParser

    from flask import Flask, current_app

    sys.path.append(os.getcwd())

    venv = os.environ.get("VIRTUAL_ENV", None)
    if venv:
        print(venv_warning, file=sys.stderr)
        if sys.platform == "win32":
            path = os.path.join(venv, 'Lib', 'site-packages')
        else:
            python = "python{}.{}".format(*sys.version_info[:2])
            path = os.path.join(venv, 'lib', python, 'site-packages')
        sys.path.insert(0, path)
        site.addsitedir(path)

    parser = ArgumentParser()
    parser.add_argument("flask_instance")
    parser.add_argument("-n", "--name", default=os.path.basename(os.getcwd()),
                        help="Postman collection name (default: current directory name)")
    parser.add_argument("-b", "--base_url", default="{{base_url}}",
                        help="the base of every URL (default: {{base_url}})")
    parser.add_argument("-a", "--all", action="store_true",
                        help="also generate OPTIONS/HEAD methods")
    args = parser.parse_args()

    logging.disable(logging.CRITICAL)

    try:
        app_path, app_name = args.flask_instance.rsplit('.', 1)
        app = getattr(__import__(app_path), app_name)
    except Exception as e:
        parser.error("can't import \"{}\" ({})".format(args.flask_instance, str(e)))

    if not isinstance(app, Flask):
        parser.error("\"{}\" is not a Flask instance".format(args.flask_instance))

    with app.app_context():
        collection = Collection(args.name)
        rules = list(current_app.url_map.iter_rules())
        for rule in rules:
            for method in rule.methods:
                if args.all or method not in ["OPTIONS", "HEAD"]:
                    endpoint = current_app.view_functions[rule.endpoint]
                    route = Route.from_werkzeug(rule, method, args.base_url)
                    route.description = trim(endpoint.__doc__)
                    collection.add_route(route)

    print(json.dumps(collection.to_dict()))


if __name__ == "__main__":
    main()
