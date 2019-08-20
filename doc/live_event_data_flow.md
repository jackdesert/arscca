Live Event Data Flow
====================

Goal
----

Push synchronization

Browser: GET /live
------------------

This page includes a complete list of drivers AND a revision.
The browser immediately connects to the websocket and sends a version_check message.


Browser Message: version_check
------------------------------

After the browser connects to the websocket, it sends a message:

    { source: 'browser',
      action: 'version_check',
      data: { version: xx }}


Browser Logic: all_drivers Message Received
-------------------------------------------

Update the drivers array in javascript and sort it by whatever
it was sorted by before.


Browser Logic: update_drivers Message Received
----------------------------------------------

The primary key for each driver is the driver name.
- Delete indicated drivers from "delete" hash
- Create indicated drivers from "create" hash
- Update any drivers in "update" hash

Note that the "create" line item must happen before the "update" line item.

Note the update hash contains all the attributes stored on the client side.


Server Logic: version_check message Received
--------------------------------------------

When the server receives a version_check message from the browser:

    if version_matches:
        do_nothing
    else:
        send_message(all_drivers)


Server Logic: jinja2_file_updated
---------------------------------

    when file_updated:
        send_message(update_drivers)



Server Message: update_drivers
------------------------------

    { source: 'server',
      action: 'update_drivers',
      data: { version: 1,
              drivers: {create: ['Josh Newfoundland'].
                        update: [{driver_name: 'Josh Newfoundland', ...},
                                 {driver_name: 'Sylvia Existentialista', ...}],
                        destroy: ['Perry Usedtobe', 'Yve Solongfarewell' } }


Server Message: all_drivers
---------------------------

    { source: 'server',
      action: 'all_drivers',
      data: { version: 1,
              drivers: [...] }



Server: When Receives version_check
