from arscca.models.calendar.base_event import BaseEvent
import pdb

class BoardMeetingEvent(BaseEvent):
    '''Board Meetings, etc'''

    # First wednesday of each month, except September is bumped to last week in August
    DATES = frozenset(['2020-03-04',
                       '2020-04-01',
                       '2020-05-06',
                       '2020-06-03',
                       '2020-07-01',
                       '2020-08-05',
                       '2020-08-26',
                       '2020-10-07',
                       '2020-12-02'])
    def __init__(self, date):
        self._date = date

    @property
    def name(self):
        return 'Board Meeting'

    @property
    def date(self):
        return self._date

    @property
    def venue(self):
        return 'Teleconference via Jitsi'

    @property
    def address(self):
        return 'https://meet.jit.si/arscca'

    @property
    def css_class(self):
        return 'meeting'

    @classmethod
    def all(cls, test_dates=None):
        '''Instantiate all rally events'''
        events = []
        dates_to_use = test_dates or cls.DATES
        for date in dates_to_use:
            event = cls(date)
            events.append(event)
        return events




