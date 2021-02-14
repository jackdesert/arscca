
ARSCCA
======

Pulls the stats from the arscca.org website and displays them.

Allows you to sort by whichever column you like.

Getting Started (Docker)
------------------------

These commands will start build the docker image and run it in a container.

    cd /path/to/repo
    sudo docker-compose build
    sudo docker-compose up

Note the docker-compose.yml in the root directory uses development.ini.
For production use:

    sudo docker-compose -f config/docker-compose-production.yml build
    sudo docker-compose -f config/docker-compose-production.yml up

Docker with Manual Containers
-----------------------------

    sudo docker network create arscca-network

    cd /path/to/this/repo

    # Build the image based on the Dockerfile
    docker build -t arscca-pyramid .

    # Create Network
    docker network create arscca-network

    # Run a new container with Redis
    docker run  --rm \
                --detach \
                --name arscca-redis \
                --network arscca-network \
                --volume reddata:/data \
                redis:5.0.7

    # Run a new container with arscca-pyramid
    # Note `bash` is specified as the command to run.
    # From there you can run
    #   pserve development.ini --reload
    docker run  -it  \
                --rm \
                --name arscca-pyramid \
                --network arscca-network \
                --publish 6543:6543 \
                --mount type=bind,source=/home/jd/p/arscca,target=/arscca-pyramid \
                --mount type=bind,source=/home/arscca,target=/home/arscca \
                arscca-pyramid:latest \
                bash

    # Run a new container with arscca-twisted
    # Note `bash` is specified as the command to run.
    # From there you can run
    #
    # Note bindmount to directory instead of file, as binding to a single
    # file, the bind is broken when the file is moved
    # See https://github.com/moby/moby/issues/15793#issuecomment-135411504
    docker run  -it  \
                --rm \
                --name arscca-twisted \
                --network arscca-network \
                --publish 6544:6544 \
                --mount type=bind,source=/home/jd/p/arscca-twisted,target=/arscca-twisted \
                --mount type=bind,source=/home/arscca,target=/home/arscca \
                arscca-twisted:latest \
                bash




Getting Started (Manually)
--------------------------

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


- Run your project.

    env/bin/pserve development.ini


Setting Environment Variables
-----------------------------

For an env var to work with docker compose, make sure it is included in docker-compose.yml,
and add it to .env (without quotes)

For an env var to work with a manual container, set it inside the container before running pserve.



Production Deploy
-----------------

Set ARSCCA_SLACK_HOOK


Streamlined Server
------------------

A streamlined server redirects from the home page to /live.
Most features of the website remain viable if you have links to them,
but the focus remains on live results.

To use this in streamlined mode, set ARSCCA_STREAMLINE


ARSCCA_AXWARE_CAPABLE
---------------------

Set this environment variable to a comma-separated list of driver slugs
to indicate which drivers (in run groups) are trained / willing to run AxWare.

    ARSCCA_AXWARE_CAPABLE=john_lenin,paul_mccartney

(To test this in development, set it explicitly from inside the container:)

    ARSCCA_AXWARE_CAPABLE=john_lenin,paul_mccartney pserve development.ini --reload

### Current List

Greg Laborde (RRR)
Jereme Mason (RRR)
Andy Chason (RRR)

Jeff Fuller ???

ARSCCA_AXWARE_CAPABLE=ben_walker,thomas_lipham,nick_mellenthin,brady_loretz,jack_desert,tom_penfound,andy_chason,jereme_mason,greg_laborde,blake_alvarado

Interested: Corey Pettet



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


Transpiling Javascript
----------------------

Run this bash script:

    bin/transpile_javascript

Some javascripts in this project are written to the ES5 spec, others
are written to ES6. ES5 browsers would throw errors when encountering
things like "let" and arrow functions. And then we got lots of notifications
of these errors via slack.

Now we (transpile)[https://www.stevefenton.co.uk/2012/11/compiling-vs-transpiling/]
all our javascripts into a single ES5-compliant file.

That is, edit the files in

    arscca/static/*.js

but the browser will load

    arscca/static/transpiled/arscca_es5.js


### Installing Babel & Friends

    sudo apt install npm
    npm install -D babel-cli
    npm install -D babel-preset-env


Also note the .babelrc file that specifies the "env" preset.



Adding a New Event
------------------

  - Publish results with bin/axware_publisher.py
  - Run bin/archive_events.py to pull new events into repo
  - Restart server
  - Click on the new event(s) so their names get loaded into redis


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

### Make sure Tests Pass

    env/bin/pytest arscca/test

### Make sure event in question parses

First verify that the event data you are testing is parseable.
Do this by visiting the page.

### Make sure event in question is from the current year

Only run a current-season event through the live parser,
because it will choose today's date, and you want PAX classes to match
actual PAX classes. (Some classes disappear from year to year)


### How to test

Then go to the arscca official results for that page,
and copy that source into /home/arscca/

If the event you are debugging requires anything other than the StandardParser,
make sure you specify that today's date use either the SingleDayParser
or the RallyParser.


Event Types
-----------
Starting with year 2017, there is an extra column

### Rally

2016-: (ONE row per driver)
    http://arscca.jackdesert.com/events/2016-11-19
    http://arscca.org/index.php?option=com_content&view=article&id=294

2016-: (TWO row per driver) (Had one extra column for car color...deleted)
    http://arscca.jackdesert.com/events/2013-04-20
    http://arscca.org/index.php?option=com_content&view=article&id=88


2017+ (ONE row per driver)
    http://arscca.jackdesert.com/events/2019-10-05
    http://arscca.org/index.php?option=com_content&view=article&id=430

2017+ (TWO rows per driver):
    Rally #6 2019
    http://arscca.jackdesert.com/events/2019-11-09
    http://arscca.org/index.php?option=com_content&view=article&id=496


### OneCourse
2016:
2017+:
    Governor's Cup 2019
    http://arscca.jackdesert.com/events/2019-10-26
    http://arscca.org/index.php?option=com_content&view=article&id=492

### TwoCourse
2016:
2017:


Event Archive
-------------

There is a module in bin/archive_event.py that pulls most events from joomla
and stores them in this repository in the archive/ directory.


Verify All Events Parse  // Load Event Names and Fond Memories into Redis
-------------------------------------------------------

    env/bin/python bin/load_event_names_and_fond_memories.py


Generate Scanner Flowchart
--------------------------

See https://www.graphviz.org/documentation/

    bin/generate_scanner_flowchart


Installing Typescript
---------------------

    sudo npm install -g typescript
    which tsc


Installing Node Dependencies
----------------------------

This will build node dependencies based on package.json and package-lock.json.

    cd /path/to/repo
    npm install


Building from TypeScript
------------------------

This project uses typescript. This builds it:


    tsc && bin/transpile_javascript && bin/browserify && echo CHAIN-OF-SUCCESS

Here's what each piece does:

  - tsc compiles to es6 modules.
  - bin/transpile_javascript uses babel to transpile to es5 for old browser support
  - bin/browserify uses browserify to build a single javascript file based on all the
    dependencies of a single entry point

(At the time of this writing, three separate entry points are used.
Which means browserify is generating three builds.)


Joomla Down
-----------

See commit 079
Joomla is down, so now this loads from a local file.
The filename looks like archive/DATE__000.html.



Backlog
-------

  * Fix Live page so it shows date based on when uploaded (or axware file created)
  * Fix bug where stale raw file is shown from live page
  * Figure out how to get svg to display with arrows on james' phone
  * Make it so you can swipe between photos on photo uploads page (Daniel's Request)
  * Document how to run all the doctests
  * Build a middleware that strips trailing slash from url
  * Move javascripts to Typescript for the experience
  * Write a module for both removing one photo at a time
    and for making a backup of what's in S3/redis
  * Write a script or classmethod for removing a photo (both from s3 and redis)
  * Add transparent border around photos that turns dark when hover
  * Redirect live.arscca.org to uno.arscca.org/live
    (or just use uno.arscca.org/live)
  * View that shows the last few pictures
    that way we can show them on the home page of arscca.org
  * Fix so that club name can be used to indicate rallycross scoring
  * If password accepted, whitelist IP address
  * Fix docker mount so that /live/raw shows updated file
  * Add "6pm All are welcome" to board meetings (all are welcome is a link)
  * Minimize line-height on small devices for calendar
  * Update styling so that on small devices the text doesn't wrap so hard
    (how about:
      Date    Location1 Details
      Name    Location2
  * Change home page of arscca.org to read "Upcoming Events" instead of "2019 season"
  * Store calendar to redis to avoid traffic on motorsportreg
  * Add bits about follow us on facebook.
  * Fix S3 tests so they return the correct prepend
  * Fix S3 tests so they break without network.


  * Find a sane way to manage redis data when running pytest
    so it does not clobber development data
  * Pass name through canon before choosing display name (fixes error below?)
  * Privacy Requests --- also see Kim Fares link below
  * Add events from http://arscca.org/201303oldsite/results.htm
  * Jon Seaton is throwing error Uncaught TypeError: Illegal invocation when loading a driver profile
  * Get /live functional again
  * New AxWare software
  * Find out why clicking link of Kim Fares on home page
    takes me to /drivers/kimberly_hodges which has photos but no events,
    and going to /drivers/kim_hodges has events but no photos
  * Find out why /drivers/gordo matches /gordon_gibson
  * on /drivers/:slug provide links to events where they did not participate
  * Update arscca.org to run /administrator over SSL
  * Kim Fares (alias) http://localhost:6543/events/2018-11-02?cb=1
  * Get rally parser to give a numerical score to DNF (instead of no score)
  * This rallyx event has empty columns after the 8 real runs: http://localhost:6543/events/2019-10-05?cb=1
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



