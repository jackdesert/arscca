arscca
======

Getting Started
---------------

- Change directory into your newly created project.

    cd arscca

- Create a Python virtual environment.

    python3 -m venv env

- Upgrade packaging tools.

    env/bin/pip install --upgrade pip setuptools requests bs4

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Run your project's tests.

    env/bin/pytest

- Run your project.

    env/bin/pserve development.ini
ARSCCA
======

Pulls the stats from the arscca.org website and displays them.

Allows you to sort by whichever column you like.


Backlog
-------

  * Assign pos_overall, pos_pas, pos_class to each driver
  * Add method to_json()
  * Add cookiecutter pyramid app



Genuine
-------

Let me know if you would like to link arscca to this site, or somehow integrate the two
