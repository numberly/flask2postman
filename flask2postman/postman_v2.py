import re

from .utils import trim, var_re


class Collection:
    def __init__(self, name, base_url, all, add_folders):
        self.name = name
        self.base_url = base_url
        self.all = all
        self.add_folders = add_folders

        self.endpoints = []
        self.folders = []

    @classmethod
    def from_flask(cls, name, base_url, all, add_folders, current_app):
        collection = cls(name, base_url, all, add_folders)

        for blueprint_name in current_app.blueprints:
            folder = Folder(blueprint_name)
            collection.add_folder(folder)

        for rule in current_app.url_map.iter_rules():
            endpoint = current_app.view_functions[rule.endpoint]
            for method in rule.methods:
                if method in ["OPTIONS", "HEAD"] and not all:
                    continue

                endpoint = Endpoint(rule, endpoint, method, base_url)
                collection.add_endpoint(endpoint)

        return collection

    def add_endpoint(self, endpoint):
        self.endpoints.append(endpoint)

    def add_folder(self, folder):
        self.folders.append(folder)

    @property
    def info(self):
        return {
            "name": self.name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        }

    @property
    def item(self):
        items = []

        for item in self.endpoints:
            if item.folder and self.add_folders:
                for folder in self.folders:
                    if folder.name == item.folder:
                        folder.endpoints.append(item)
            else:
                items.append(item)

        if self.add_folders:
            for folder in self.folders:
                items.append(folder)

        return [item.to_dict() for item in items]

    def to_dict(self):
        return {
            "info": self.info,
            "item": self.item
        }


class Folder:
    def __init__(self, name):
        self.name = name
        self.endpoints = []

    @property
    def item(self):
        return [item.to_dict() for item in self.endpoints]

    def to_dict(self):
        return {
            "name": self.name,
            "items": self.item
        }


class Endpoint:
    def __init__(self, rule, endpoint, method, base_url):
        self.rule = rule
        self.endpoint = endpoint
        self.base_url = base_url

        self.method = method
        self.description = trim(endpoint.__doc__)

    @property
    def name(self):
        return self.rule.endpoint.rsplit('.', 1)[-1] \
            .split("_", 1)[-1] \
            .replace("_", " ")

    @property
    def url(self):
        url = self.base_url + self.rule.rule
        for match in re.finditer(var_re, url):
            var = match.group("var")
            var_name = "{{" + match.group("var_name") + "}}"
            url = url.replace(var, var_name)
        return url

    @property
    def folder(self):
        if "." in self.rule.endpoint:
            folder_name, _ = self.rule.endpoint.split('.', 1)
            return folder_name

        return None

    def to_dict(self):
        return {
            "name": self.name,
            "request": {
                "url": self.url,
                "method": self.method,
                "description": self.description
            }
        }
