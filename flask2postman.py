#!/usr/bin/env python
from __future__ import print_function

import re
import sys
from copy import copy
from time import time
from uuid import uuid4

__version__ = "1.1.1"

methods_order = ["GET", "POST", "PUT", "PATCH", "DELETE", "COPY", "HEAD",
                 "OPTIONS", "LINK", "UNLINK", "PURGE"]

var_re = re.compile(r"(?P<var><[a-zA-Z0-9_]+:(?P<var_name>[a-zA-Z0-9_]+)>)")

venv_warning = ("WARNING: Attempting to work in a virtualenv. If you encounter "
                "problems, please install flask2postman inside the virtualenv.")


PY2 = sys.version_info[0] < 3
if PY2:
    maxint = sys.maxint
else:
    maxint = sys.maxsize


def get_time():
    return int(round(time() * 1000))


class Collection:

    def __init__(self, name):
        self.id = str(uuid4())
        self._requests = []
        self._folders = []
        self.name = name
        self.timestamp = get_time()

    def reorder_requests(self):
        def _get_key(request):
            return str(methods_order.index(request.method)) + request.name
        self._requests = sorted(self._requests, key=_get_key)

    def add_folder(self, folder):
        folder._collection = self
        folder.collection_id = self.id
        folder.collection_name = self.name
        self._folders.append(folder)
        self.reorder_requests()

    def add_route(self, route):
        route.collection_id = self.id
        self._requests.append(route)
        self.reorder_requests()

    @property
    def order(self):
        return [request.id for request in self._requests if request.folder is None]

    @property
    def requests(self):
        return [request.to_dict() for request in self._requests]

    @property
    def folders(self):
        return [folder.to_dict() for folder in self._folders]

    def to_dict(self):
        d = copy(self.__dict__)
        d.pop("_requests")
        d.pop("_folders")
        d.update(requests=self.requests, order=self.order)
        if len(self.folders) > 0:
            d.update(folders=self.folders)
        return d


class Folder:
    _folders_ = dict()

    def __init__(self, name):
        self.id = str(uuid4())
        self._collection = None
        self._requests = []
        self.name = name

    def add_route(self, route):
        route.folder = self.id
        self._collection.add_route(route)
        self._requests.append(route)
        self.reorder_requests()

    def reorder_requests(self):
        def _get_key(request):
            return str(methods_order.index(request.method)) + request.name
        self._requests = sorted(self._requests, key=_get_key)

    @property
    def order(self):
        return [request.id for request in self._requests]

    def to_dict(self):
        d = copy(self.__dict__)
        d.pop("_requests")
        d.pop("_collection")
        d["collectionId"] = d.pop("collection_id")
        d["collectionName"] = d.pop("collection_name")
        d.update(order=self.order)
        return d

    @staticmethod
    def get_or_create_folder(collection, name):
        folder = Folder._folders_.get(name)
        if folder is not None:
            return folder
        else:
            folder = Folder(name)
            collection.add_folder(folder)
            Folder._folders_[name] = folder
            return folder


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
        self.folder = None
        self.time = get_time()
        self.url = url

    def to_dict(self):
        d = copy(self.__dict__)
        d["collectionId"] = d.pop("collection_id")
        d["dataMode"] = d.pop("data_mode")
        if self.folder is None:
            d.pop("folder")
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
    indent = maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    trimmed = [lines[0].strip()]
    if indent < maxint:
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
    parser.add_argument("-i", "--indent", action="store_true",
                        help="indent the output")
    parser.add_argument("-f", "--folders", action="store_true",
                        help="add Postman folders for blueprints")
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
                    folder_name = rule.endpoint.rsplit('.', maxsplit=2)
                    if len(folder_name) >= 2 and args.folders:
                        folder = Folder.get_or_create_folder(collection, folder_name[0])
                        folder.add_route(route)
                    else:
                        collection.add_route(route)

    if args.indent:
        json = json.dumps(collection.to_dict(), indent=4, sort_keys=True)
    else:
        json = json.dumps(collection.to_dict())

    print(json)


if __name__ == "__main__":
    main()
