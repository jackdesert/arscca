# Axware

## Create Event


AxWare is happier if you create all your events for a season in the same directory.
That way your stylesheets and class definitions are the same for the entire season.

If, on the other hand, you create a new directory for each event, it will
make a copy of the stylesheets and class definitions from whatever folder
you saved your last event in. And pretty soon you have several copies
of all these files. (And none of them are linked)

Export Registrations from Motorsportreg
---------------------------------------

- Go to motorsportreg.com.
- Click Organizers.
- Log in.
- Click Reports.
- Select Axware Event Export (current)
- Choose the event from the dropdown.
- Scroll to the bottom and click Continue.
- Click Export.
- Choose TAB separated values.
- Click Export Report

## Import Registrations

Click File -> Import -> Registration.

The expected format is TAB separated value. (CSV won't work)

If you don't see any drivers added to the event,
click View -> Registration Log
(You may want to clear the log, then try the import again)

Count the drivers in AxWare and make sure it matches the number of lines in the file
you imported. (Motorsportreg has a bug where it lets people register with same class & number,
and Axware drops duplicates on the floor.)

## Class Definitions

The class definitions are in the data directory with the extension .def.

It appears to be a tab-delimited text file.

To edit the base file (in the data directory), close the event you are in,
then click Edit -> Class Definitions. Then use the **Browse** button.

To edit just the file for your current event, you can leave the event open
and click Edit -> Class Definitions.


## Name Order

Setup -> Options -> Event Settings -> Name Order

## Change Number of Runs for an Event

Setup -> Modify Event Attributes

Note: Number of runs is RUNS PER DAY


## What does Consolidated mean?

Raw data is stored in the staging grid.
Consolidated data is stored in the registration grid (It's synonymous with "standings")


## Verify that everyone has a Barcode

Sort the registration grid by member number and look for anyone with a blank

## Update Member Number

The registration grid is a glorified excel spreadsheet. You can type right in it.


## Why does the registration grid move when a driver crosses the finish line?

The registration grid is also the standings grid, so it sorts
by who's fastest.

## Announcer Window

Timing -> Start Announcer Window.

This opens another screen.
