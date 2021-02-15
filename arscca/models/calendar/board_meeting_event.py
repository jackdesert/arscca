from arscca.models.calendar.base_event import BaseEvent
import pdb

class BoardMeetingEvent(BaseEvent):
    '''Board Meetings, etc'''

    # First wednesday of each month, except September is bumped to last week in August
    DATES = frozenset(['2021-03-03',
                       '2021-04-07',
                       '2021-05-05',
                       '2021-06-02',
                       '2021-07-07',
                       '2021-08-04',
                       '2021-09-01',
                       '2021-10-06',
                       '2021-12-02'])
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
        return ''

    @property
    def info(self):
        return '6:30pm'

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

    @property
    def jitsi(self):
        return True



