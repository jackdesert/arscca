from bs4 import BeautifulSoup
from arscca.models.calendar.default_rally_event import DefaultRallyEvent
from unittest import TestCase

class TestDefaultRallyEvent(TestCase):
    def test_attributes(self):
        event = DefaultRallyEvent('2020-12-13', 'Fun Run City', 'Celine Dion')
        assert event.date  == '2020-12-13'
        assert event.name  == 'Fun Run City'
        assert event.chair == 'Celine Dion'

    def test_events_not_in_motorsportreg(self):
        test_rally_calendar = (('2020-02-22', 'RallyX Test & Tune', 'Zach Shaddox'),
                               ('2020-03-14', 'RallyX 1',           'Nelson Santos'),)


        dates_in_motorsportreg = ['2020-02-22']

        events = DefaultRallyEvent.events_not_in_motorsportreg(dates_in_motorsportreg,
                                                      test_rally_calendar=test_rally_calendar)
        assert len(events) == 1
        assert events[0].date == '2020-03-14'
