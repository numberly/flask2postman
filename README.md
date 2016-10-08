[Postman]: https://www.getpostman.com/
[Flask]: http://flask.pocoo.org/

# flask2postman

![Build Status](https://img.shields.io/pypi/v/flask2postman.svg)
![Build Status](https://img.shields.io/pypi/status/flask2postman.svg)

A tool that creates a [Postman] collection from a [Flask] application.

## Install

```sh
$ pip install flask2postman
```

## Example

Let's say that you have a Flask project called "example" (see `example.py`), 
and you want to generate a Postman collection out of it.

You just need to tell `flask2postman` how to import the Flask instance,
and optionally give a name to the Postman collection:

```sh
$ flask2postman example.app --name "Example Collection" --folders > example.json
```

If you don't have a global Flask instance but rather use a function to
initialize your application, that works too:

```sh
$ flask2postman example.create_app --name "Example Collection" --folders > example.json
```

This will generate the JSON configuration, and write it into the `example.json` file. 
You can then import this file into Postman ("Import Collection" button), and profit:

![Postman screenshot](https://raw.githubusercontent.com/1000mercis/flask2postman/42d20fe89d9d1f831bbfbe6275471e624d40c488/img/screenshot.jpg)

On a side note, you can see that endpoint's docstrings are automatically
imported as descriptions.

## Usage

```sh
usage: flask2postman [-h] [-n NAME] [-b BASE_URL] [-a] [-i] [-f]
                     flask_instance

positional arguments:
  flask_instance

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Postman collection name (default: current directory
                        name)
  -b BASE_URL, --base_url BASE_URL
                        the base of every URL (default: {{base_url}})
  -a, --all             also generate OPTIONS/HEAD methods
  -s, --static          also generate /static/{{filename}} (Flask internal)
  -i, --indent          indent the output
  -f, --folders         add Postman folders for blueprints
```

## License

MIT