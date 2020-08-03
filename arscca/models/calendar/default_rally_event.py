from arscca.models.calendar.base_event import BaseEvent
from datetime import date
import pdb
import re




class DefaultRallyEvent(BaseEvent):
    '''Rally events are known, but not all are in motorsportreg yet
    This class allows us to fill in the blanks'''

    #                  DATE          NAME                  CHAIR
    RALLY_CALENDAR = (('2020-02-22', 'RallyX Test & Tune', 'Zach Shaddox'),
                      ('2020-03-14', 'RallyX 1',           'Nelson Santos'),
                      ('2020-04-18', 'RallyX 2',           'Dakota Waters'),
                      ('2020-05-30', 'RallyX 3',           'Phil Rucker'),
                      #('2020-06-27', 'RallyX 4',           'Dakota Waters'),
                      ('2020-08-29', 'RallyX 5',           ''), # Jack
                      ('2020-09-19', 'RallyX 6',           ''),
                      ('2020-10-24', 'RallyX 7',           ''), # Shaddox
                      ('2020-11-21', 'RallyX 8',           ''), # Nelson
                     )

    def __init__(self, date, name, chair):
        self._date = date
        self._name = name
        self._chair = chair

    @property
    def date(self):
        return self._date

    @property
    def name(self):
        return self._name

    @property
    def chair(self):
        return self._chair

    @property
    def css_class(self):
        return 'rallyx'

    @property
    def address(self):
        return 'Clinton, AR'

    @classmethod
    def events_not_in_motorsportreg(cls, dates_in_motorsportreg, test_rally_calendar=None):
        '''Instantiate a DefaultRallyEvent for each date listed in
        RALLY_CALENDAR that is not in motorsportreg_dates'''

        rally_calendar = test_rally_calendar or cls.RALLY_CALENDAR
        events = []
        dates = frozenset(dates_in_motorsportreg)
        for date, name, chair in rally_calendar:
            if not date in dates:
                event = cls(date, name, chair)
                events.append(event)
        return events


