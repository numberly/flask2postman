from flask import Flask

app = Flask(__name__)


@app.route("/foo", methods=["GET"])
def get_foo(self):
    return "foo"


@app.route("/foo/<int:id>", methods=["PATCH"])
def patch_foo(self):
    return "", 200


@app.route("/bar", methods=["GET", "POST", "PUT"])
def bar(self):
    return "", 501
