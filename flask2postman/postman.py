import re

from .utils import trim

var_re = re.compile(r"(?P<var><([a-zA-Z0-9_]+:)?(?P<var_name>[a-zA-Z0-9_]+)>)")


class Collection:

    def __init__(self, args):
        self.args = args
        self.items = []

    def add_rules(self, current_app):
        for rule in current_app.url_map.iter_rules():
            endpoint = current_app.view_functions[rule.endpoint]
            for method in rule.methods:
                if method in ["OPTIONS", "HEAD"] and not self.args.all:
                    continue

                item = Item(rule, endpoint, method, self.args)
            self.items.append(item)

    @property
    def info(self):
        return {
            "name": self.args.name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        }

    @property
    def item(self):
        return [item.to_dict() for item in self.items]

    def to_dict(self):
        return {
            "info": self.info,
            "item": self.item
        }


class Item:

    def __init__(self, rule, endpoint, method, args):
        self.rule = rule
        self.endpoint = endpoint
        self.method = method
        self.description = trim(endpoint.__doc__)

    @property
    def name(self):
        return self.rule.endpoint.rsplit('.', 1)[-1] \
            .split("_", 1)[-1] \
            .replace("_", " ")

    @property
    def url(self):
        url = self.args.base_url + self.rule.rule
        for match in re.finditer(var_re, url):
            var = match.group("var")
            var_name = "{{" + match.group("var_name") + "}}"
            url = url.replace(var, var_name)
        return url

    def to_dict(self):
        return {
            "name": self.name
        }
