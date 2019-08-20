
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

- Pip install from requirements.txt

    env/bin/pip install -r requirements.txt

    # Uses these packages:
    # pip setuptools requests bs4 redis plim matplotlib

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Run your project's tests.

    env/bin/pytest

- Run your project.

    env/bin/pserve development.ini


National Events
---------------

See related repository, named arscca-pdf, for generating CSV files from
the pdfs produced by SCCA.


Gossip
------

To add driver gossip, create or update the file:

    templates/gossip/<driver_slug>.plim



Requirements.txt
----------------

When you generate requirements.txt, make sure you use the --exclude-editable flag

    env/bin/pip freeze --exclude-editable > requirements.txt

Otherwise an arscca egg will be created, and you may end up serving stale code
in production.


Backlog
-------

  * replace Infinity with '-'
  * Use production vue.js
  * Remove unneeded pieces from handlebars
  * Show ties in standings when two people both have 5 points
  * Consistent sorting order in case of ties for easy compare dev vs production
  * Aliases for driver names for Standings so Nick/Nicholas share credit
  * Adapt Feedback link to be noticeable on HUGE WIDE SCREENS
  * Footer that looks like a footer (instead of contact info for a driver)
  * Throw error in development mode if totals do not add up
  * Add error checking that compares my math to master time??
  * Dynamicize links to "PAX SOURCE DATA" on each page to use the correct year
  * Decide whether to skip event 3 or not (numbering convention)
  * canonize name in season points report
  * Make heading text smaller on smaller devices (so page__title does not wrap)
  * Render also in html (at least basic version)
  * List with Yandex and Google
  * After new stats become available, post new mashup facebook @arscca
  * robots.txt
  * advertise
  * Make it easy to see classes grouped together (stripe??)
  * Allow highlight a single driver (This interaction design may need
    me to observe several people using the site so I can see if they intuit
    how it works)



Genuine
-------

Let me know if you would like to link arscca to this site, or somehow integrate the two

Jack Desert
Data Scientist
Web Engineer
*Race Engineer*






