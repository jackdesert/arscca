
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

    env/bin/pip install --upgrade pip setuptools requests bs4 redis

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Run your project's tests.

    env/bin/pytest

- Run your project.

    env/bin/pserve development.ini


Backlog
-------

  * Ask if there are any legal issues with posting results
  * After new stats become available, post new mashup facebook @arscca
  * robots.txt
  * advertise
  * View your own source code to make sure <header>, etc are in order
  * Move content close to top
  * Advertise it!
  * Make it easy to see classes grouped together (stripe??)
  * Find canonical spelling of pax Pax PAX and spell all columns the same


  * Cache JSON blob (drivers) in redis (for an hour or so)
    - so can handle way more traffic
  * Put a Mutex around the network call so a spike in traffic
    will still only call external site once
  * Last-modified is available..



Genuine
-------

Let me know if you would like to link arscca to this site, or somehow integrate the two

Jack Desert
Data Scientist
Web Engineer
*Race Engineer
