from flask import Flask, Blueprint

app = Flask(__name__)


@app.route("/foo", methods=["GET"])
def get_foo():
    """Get some foo.

    Returns:
        A string contaning a nice foo.
    """
    return "foo"


@app.route("/foo/<int:id>", methods=["PATCH"])
def patch_foo(id):
    return "", 200


@app.route("/bar", methods=["GET", "POST", "PUT"])
def bar():
    return "", 501


baz = Blueprint("baz", __name__)


@baz.route("/baz", methods=["GET"])
def get_baz():
    return "baz"


app.register_blueprint(baz)

if __name__ == "__main__":
    app.run()
