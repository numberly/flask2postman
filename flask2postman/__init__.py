import os
import sys
from importlib import import_module

from flask2postman.utils import init_virtualenv
from flask2postman.postman_v1 import Collection as CollectionV1
from flask2postman.postman import Collection
__version__ = "1.4.3"


def main():
    import json
    import logging
    from argparse import ArgumentParser

    from flask import Flask, current_app

    sys.path.insert(0, os.getcwd())
    init_virtualenv()

    parser = ArgumentParser()
    parser.add_argument("flask_instance")
    parser.add_argument("-n", "--name", default=os.path.basename(os.getcwd()),
                        help="Postman collection name (default: current directory name)")
    parser.add_argument("-b", "--base_url", default="{{base_url}}",
                        help="the base of every URL (default: {{base_url}})")
    parser.add_argument("-a", "--all", action="store_true",
                        help="also generate OPTIONS/HEAD methods")
    parser.add_argument("-s", "--static", action="store_true",
                        help="also generate /static/{{filename}} (Flask internal)")
    parser.add_argument("-v1", "--export-as-v1", action="store_true",
                        help="export using Postman schema v1.0.0 instead of v2.1.0")
    parser.add_argument("-i", "--indent", action="store_true",
                        help="indent the output")
    parser.add_argument("-f", "--folders", action="store_true",
                        help="add Postman folders for blueprints")
    args = parser.parse_args()

    logging.disable(logging.CRITICAL)

    try:
        app_path, app_name = args.flask_instance.rsplit('.', 1)
        app = getattr(import_module(app_path), app_name)
    except Exception as e:
        msg = "can't import \"{}\": {}"
        parser.error(msg.format(args.flask_instance, str(e)))

    if not isinstance(app, Flask):
        try:
            app = app()
        except Exception:
            pass
        if not isinstance(app, Flask):
            msg = '"{}" is not (or did not return) a Flask instance (type: {})'
            parser.error(msg.format(args.flask_instance, type(app)))

    with app.app_context():
        if args.export_as_v1:
            collection = CollectionV1(args)
        else:
            collection = Collection(args)
        collection.add_rules(current_app)

    if args.indent:
        json = json.dumps(collection.to_dict(), indent=4, sort_keys=True)
    else:
        json = json.dumps(collection.to_dict())

    print(json)


if __name__ == "__main__":
    main()
