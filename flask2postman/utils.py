import os
import re
import site
import sys


PY2 = sys.version_info[0] < 3
if PY2:
    maxint = sys.maxint
else:
    maxint = sys.maxsize

venv_warning = ("WARNING: Attempting to work in a virtualenv. If you encounter "
                "problems, please install flask2postman inside the virtualenv.")

var_re = re.compile(r"(?P<var><([a-zA-Z0-9_]+:)?(?P<var_name>[a-zA-Z0-9_]+)>)")


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


# ramnes: shamelessly stolen from IPython
def init_virtualenv():
    venv = os.environ.get("VIRTUAL_ENV", None)
    if not venv:
        return

    p = os.path.normcase(sys.executable)
    paths = [p]
    while os.path.islink(p):
        p = os.path.normcase(os.path.join(os.path.dirname(p), os.readlink(p)))
        paths.append(p)
    venv_path = os.path.normcase(venv)
    if any(p.startswith(venv_path) for p in paths):
        return

    print(venv_warning, file=sys.stderr)
    if sys.platform == "win32":
        path = os.path.join(venv, 'Lib', 'site-packages')
    else:
        python = "python{}.{}".format(*sys.version_info[:2])
        path = os.path.join(venv, 'lib', python, 'site-packages')
    sys.path.insert(0, path)
    site.addsitedir(path)
