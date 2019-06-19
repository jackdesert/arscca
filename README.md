
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

    env/bin/pip install --upgrade pip setuptools requests bs4 redis plim

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

requirements.txt is not being used (yet) in this project because `pip freeze` 
creates an arscca egg, which appears to lead to the source code being copied 
to env/src, which leads to deployment headaches because you change what's in git
and the stale code in env/src runs instead...

TODO: Figure out how to use requirements.txt without source code being copied

Backlog
-------

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
  * Maybe we want to be able to highlight multiple drivers?



Genuine
-------

Let me know if you would like to link arscca to this site, or somehow integrate the two

Jack Desert
Data Scientist
Web Engineer
*Race Engineer*


Backlog
-------

Throw error in development mode if totals do not add up
Add apology message at top of page
Add note at bottom of page saying that 39+1 == 41
Add error checking that compares my math to master time??
Dynamicize links to "PAX SOURCE DATA" on each page to use the correct year



