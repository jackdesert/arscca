Live Event Data Flow
====================

Goal
----

Push synchronization such that the web page accurately displays the names and
times from the live event.

The Basics (Naive Approach)
---------------------------

When a web browser loads, it fetches drivers via HTTP from pyramid.
This includes a revision.

When the browser opens a websocket connected to twisted-server,
the twisted-server sends updates to the browser whenever the event
is updated. Twisted-server includes the revision with any changes
so the browser can tell whether it is in sync.


Possible Race Conditions
------------------------


When the browser loads the page and initializez the websocket, because of race
condition, either the revision loaded via HTTP or the update received through
the websocket could be either ahead or behind the other.

### Scenario 1

The following situation could be problematic:
  - Browser loads revision 121 of DRIVERS over HTTP
  - Update from twisted-server comes through with revision 123.

In the above scenario, we are missing revision 122.


### Scenario 2

Another situation that is easier to deal with:
  - Browser loads revision 52 of DRIVERS over HTTP
  - Update from twisted-server comes through with revision 52 or lower.

In this case, the browser can simply not apply the revisions that
are less than or equal to the revision it has already loaded.



Overlap Methodology
-------------------

In order to skirt around possible race conditions outlined above,
this project uses an "overlap" methodology. On connect, twisted-server
automatically sends the last N updates to the browser, and each update
includes a revision number.

The browser can ignore any updates that it already has (as by comparing revisions).

And in the case where a revision arrives from twisted-server that is more
than one greater than the current revision held by the browser,
the browser knows something is amiss and it will start over.

Starting over looks like this:

  - close websocket
  - set drivers = [] so webpage clears
  - fetch all drivers over HTTP and apply preexisting sorting
  - open websocket anew


Browser: GET /live
------------------

This is an HTTP request that returns HTML.
This page does not include drivers or revision.
The reason is so that drivers always come through the same avenue,
that is: a separate AJAX request.


Browser: Get /live/drivers
--------------------------

This is an HTTP request that returns JSON.

    { 'drivers': [...],
      'revision': <int> }

The browser creates the html table.
The browser stores the revision.
The browser then opens a websocket to twisted-server.


Twisted-Server: On Connect
--------------------------

  - Send last N updates, each as separate message with revision.


Twisted-Server: On File Change
------------------------------

  - Tell Pyramid-Server to update drivers in Redis
  - Send message to all connected websocket clients with driver changes and revision


Twisted-Server: Message Format
------------------------------

There is only one message format that is sent over the Websocket.
It is always sent from twisted-server to the browser.

      { version: 1,
        drivers: {create: ['Josh Newfoundland'].
                  update: [{driver_name: 'Josh Newfoundland', ...},
                           {driver_name: 'Sylvia Existentialista', ...}],
                  destroy: ['Perry Usedtobe', 'Yve Solongfarewell' } }


Browser: On Message Received
----------------------------

Here are the steps to updating drivers based on a message:
Note the primary key for each driver is the driver name.

    def apply_changes(message):
        - Delete indicated drivers from "delete" hash
        - Create indicated drivers from "create" hash
        - Update any drivers in "update" hash



Here is the logic for determining whether a particular message should
be applied or not, based on its revision:

    if revision_in_message <= stored_revision:
        do_nothing()
    elif revision_in_message = stored_revision + 1:
        stored_revision = revision_in_message
        apply_revision()
    else:
        close_websocket_and_start_over()

