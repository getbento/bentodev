BentoDev - BentoBox Local Theme Editor
######################################

.. contents::

.. section-numbering::


Main Features
=============

* Edit BentoBox themes locally
* Uses real data when making themes
* Use Flask to act as a proxy between server requests
* Uses Jinja2 to rigidly enforce template edits

Installation
============

NOTE: This package is currently only supported on POSIX systems. For those on Windows it is recommended to create a new Vagrant box before installing.

It is recommended to install `bentodev` on a seperate Python 3 virtual environment.

For use with `Pipenv`

.. code-block:: bash

  $ pipenv --three
  $ pipenv install bentodev

For use with `venv`

.. code-block:: bash

  $ python3 -m venv venv
  $ source venv/bin/activate
  $ pip install bentodev

Usage
===========
BentoDev functions are activated via a command line interface.

.. code-block:: bash

    $ bentodev
    Usage: bentodev [OPTIONS] COMMAND [ARGS]...

    BentoDev Used to develop themes locally for BentoBox sites!

    Options:
    --version  Show the version and exit.
    --help     Show this message and exit.

    Commands:
      clone   Clone an account you have access too.
      config  Base configuration
      list    List accounts and themes you have access too.
      start   Begin running the development server

Setup
-----
Upon using BentoDev for the first time you will be prompted to use add your BentoBox account.

You may also be asked for a password to get a remote token for your session.


Cloning Themes
--------------
By using the command ``bentodev list`` or ``bentodev start`` you will see the list of available Accounts and their current associated theme.

If you do not see any Accounts/Themes you need to create an Account that is associated to your User through the BentoBox website.

To work on an Account's theme you must first clone the theme. To do so use:

.. code-block:: bash

  $ bentodev clone <theme_name>

You may be prompted to connect your GitHub account to BentoBox if you have not done so previously.

The theme will then be cloned to the ``~/bentodev/sites/<theme_name>`` folder, where you can then push edits with standard git commands.

Working on Themes
-----------------
Once a theme has been cloned you can then run a small local server that will handle making requests to BentoBox.

.. code-block:: bash

   $ bentodev start <account_name>

You should then see the server run, where you can connect at `localhost:5000 <http://localhost:5000>`_

Local Development
=================

Working with Local BentoBox
---------------------------
To use all debugging tools, create new features, or use local data, we can switch which server `bentodev` gets data from. The `--local` flag will use the `HOST` and `PORT` user configuration to access a local BentoBox Django server. Example below:

.. code-block:: bash

   $ bentodev start <account_name> --local

Working on `bentodev`
---------------------

Setup for Local Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~
To make changes to `bentodev` please clone the repository, then with a separate virtual environment, install it as a local dependency.

.. code-block:: bash

   $ git clone git@github.com:getbento/bentodev.git
   $ mkdir bentodev-local/ && cd bentodev-local && pipenv --three && pipenv shell
   $ pipenv install -e ../path/to/cloned/pipenv

This will clone bentodev, create a new virtualenv, and install the local bentodev to that environment.

Then, changes made will be reflected in the running application when using the newly created virtual environment.

Deploying bentodev Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

TO DEPLOY THOSE CHANGES to the `bentodev PyPi repo <https://pypi.org/project/bentodev/>`_, ensure that the dev dependencies from `bentodev`s Pipfile are installed to a virtual environment or are on your system. Mainly, `setuptools` and `twine` are required for deployment. Bump the version inside: `bentodev/__version__.py`.

Assuming deps and PyPi configuration is complete, run the following to update the repository:

.. code-block:: bash

   $ python setup.py upload

User Configuration
==================

Additional user settings can be added to the user config file at ``~/bentodev/config.json``. Default settings include:

.. code-block:: javascript

  {
    "BENTO_USER": "<user_name>"
  }

Additional settings can be added by hand. These include

.. code-block:: javascript

  {
    "DEV_ROOT": "<dir_pat>", (ie. "/Users/<user>/test_folder/")
    "HOST": "<host_value>", (i.e and default "0.0.0.0")
    "PORT": "<port_value>", (i.e and default "8000")
  }

Meta
====

User support
------------

Please use the following support channels:

* `GitHub issues <https://github.com/getbento/bentodev/issues>`_
  for bug reports and feature requests.
* `StackOverflow <https://stackoverflow.com>`_
  to ask questions (please make sure to use the
  `bentodev <http://stackoverflow.com/questions/tagged/bentodev>`_ tag).
* Tweet directly to `@bentoboxnyc <https://twitter.com/bentoboxnyc>`_.

Related projects
----------------

BentoBox
~~~~~~~~~~~~
The entire utility is completely coupled to the `BentoBox Django Application <https://www.github.com/getbento/bentobox>`_.

It pulls data from the production (or a local) BentoBox instance and allows real data to displayed as engineers/designers edit themes that are displayed on the getbento.com domain.

Dependencies
~~~~~~~~~~~~

* `Flask <https://http://flask.pocoo.org>`_
* `Jinja2 <http://jinja.pocoo.org/>`_
* `Requests <https://python-requests.org>`_
