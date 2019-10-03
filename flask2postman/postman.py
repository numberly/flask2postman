class Collection:

    def __init__(self, args):
        self.name = args.name
        self.items = []

    def add_rules(self, current_app):
        pass

    @property
    def info(self):
        return {
            "name": self.name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        }

    def to_dict(self):
        return {
            "info": self.info,
            "item": self.items
        }
