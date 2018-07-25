
ARSCCA
======

Pulls the stats from the arscca.org website and displays them.

Allows you to sort by whichever column you like.


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


Backlog
-------

  * Assign pos_overall, pos_pas, pos_class to each driver
  * Styling
  * Indicate which column is sorted (side borders??)
  * Make it easy to see classes grouped together (stripe??)
  * Capitalize class name in CSS
  * Display Infinity as blank



Genuine
-------

Let me know if you would like to link arscca to this site, or somehow integrate the two

Jack Desert
Data Scientist
Web Engineer
*Race Engineer
