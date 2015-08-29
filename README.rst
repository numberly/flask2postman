.. _Postman: https://www.getpostman.com/
.. _Flask: http://flask.pocoo.org/

=============
flask2postman
=============

A tool that creates a Postman_ collection from a Flask_ application.


Install
=======

.. code-block:: sh

    $ pip install flask2postman


Example
=======

We have a Flask project called "example", (see :code:`example.py`), and we want
to generate a Postman collection out of it.

We just need to tell :code:`flask2postman` how to import the Flask instance, and
optionally give a name to the collection:

.. code-block:: sh

    $ flask2postman example.app --name "Example Collection" --folders > example.json

This will generate the JSON configuration, and write it into the
:code:`example.json` file.

Then we just have to import this file into Postman ("Import Collection" button),
and profit:

.. image:: https://raw.githubusercontent.com/1000mercis/flask2postman/master/img/screenshot.jpg
    :alt: Postman screenshot

On a side note, you can see that endpoint's docstrings are automatically
imported as descriptions.


Usage
=====

.. code-block:: sh

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
      -i, --indent          indent the output
      -f, --folders         add Postman folders for blueprints


License
=======

MIT
