
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
    # pip setuptools requests bs4 redis plim matplotlib selenium

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Run your project's tests.

    env/bin/pytest

- Run your project.

    env/bin/pserve development.ini


Production Deploy
-----------------

Set the ARSCCA_SLACK_HOOK in config/environment.txt

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



Performance
-----------

If you are hosting this on a T2 or T3 instance on AWS, note that these instance
types are CPU burstable. That means it will appear performant when you parse
a single event, but if you turn on bin/demo_cp and let it run for a long time,
your CPU burst credits may run out.

On a t2.nano, which has a baseline rate of 5%, it takes about 15 seconds to parse a single event with 66 drivers.
When burst credits are available, it runs in about 400ms.

Supposedly burst credits go away on restart, so if you want to see baseline performance,
you may simply restart the box.

### arscca-twisted Timeout

If you are seeing timeouts on arscca-twisted, it may be that you have run out
of burst credits.

### ssh Performance

Note that when you have no CPU burst credits available, it also takes longer
to do things like ssh into the box, open documents in vim, etc.


Things to Test
--------------

 - Histogram is smart about choosing bin width for rallyx events
 - Red line displays between am and pm runs for standard event
 - does Parser.rank_drivers do the right thing for all three event types.
   (note it is still referencing best_combined)
 - find all references to: and replace with appropriate primary_score / secondary_score
        return self.best_combined()
        return self.best_combined_pax()
        return self.best_run()
        return self.best_run_pax()



AxWare Publisher
----------------

There is a utility for publishing AxWare results to our Joomla site:

    env/bin/python bin/axware_publisher.py


Debugging Live
--------------

Only run a current-season event through the live parser,
because it will choose today's date, and you want PAX classes to match
actual PAX classes. (Some classes disappear from year to year)

First verify that the event data you are testing is parseable.
Do this by visiting the page.

Then go to the arscca official results for that page,
and copy that source into /home/arscca/

If the event you are debugging requires anything other than the StandardParser,
make sure you specify that today's date use either the SingleDayParser
or the RallyParser.



Backlog
-------

  * Update arscca.org to run /administrator over SSL
  * Blue background for rallyx events on driver profile
  * On each driver profile, provide links to all the events that driver competed in
  * Static events for rallyx
    - update axware
  * Show ties in standings when two people both have 5 points
  * Consistent sorting order in case of ties for easy compare dev vs production
  * Adapt Feedback link to be noticeable on HUGE WIDE SCREENS
  * Footer that looks like a footer (instead of contact info for a driver)
  * Make heading text smaller on smaller devices (so page__title does not wrap)
  * Render also in html (at least basic version)
  * List with Yandex and Google
  * After new stats become available, post new mashup facebook @arscca
  * robots.txt
  * advertise
  * Make it easy to see classes grouped together (stripe??)



