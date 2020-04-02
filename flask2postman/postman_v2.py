import re

from .utils import trim

var_re = re.compile(r"(?P<var><([a-zA-Z0-9_]+:)?(?P<var_name>[a-zA-Z0-9_]+)>)")


class Collection:

    def __init__(self, name, base_url, all, add_folders):
        self.name = name
        self.base_url = base_url
        self.all = all
        self.add_folders = add_folders

        self.blueprints = []
        self.items = []

    def add_rules(self, current_app):
        for blueprint_name in current_app.blueprints:
            folder = Folder(blueprint_name)
            self.blueprints.append(folder)

        for rule in current_app.url_map.iter_rules():
            endpoint = current_app.view_functions[rule.endpoint]
            for method in rule.methods:
                if method in ["OPTIONS", "HEAD"] and not self.all:
                    continue

                item = Item(rule, endpoint, method, self.base_url)
            self.items.append(item)

    @property
    def info(self):
        return {
            "name": self.name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        }

    @property
    def item(self):
        items = []

        for item in self.items:
            if item.blueprint and self.add_folders:
                for blueprint in self.blueprints:
                    if blueprint.name == item.blueprint:
                        blueprint.items.append(item)
            else:
                items.append(item)

        if self.add_folders:
            for blueprint in self.blueprints:
                items.append(blueprint)

        return [item.to_dict() for item in items]

    def to_dict(self):
        return {
            "info": self.info,
            "item": self.item
        }


class Folder:

    def __init__(self, name):
        self.name = name
        self.items = []

    @property
    def item(self):
        return [item.to_dict() for item in self.items]

    def to_dict(self):
        return {
            "name": self.name,
            "items": self.item
        }


class Item:

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
    def blueprint(self):
        if "." in self.rule.endpoint:
            blueprint_name, _ = self.rule.endpoint.split('.', 1)
            return blueprint_name

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
