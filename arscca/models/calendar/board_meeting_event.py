from arscca.models.calendar.base_event import BaseEvent
import pdb

class BoardMeetingEvent(BaseEvent):
    '''Board Meetings, etc'''

    # First wednesday of each month, except September is bumped to last week in August
    DATES = frozenset(['2022-02-02',
                       '2022-03-02',
                       '2022-04-06',
                       '2022-05-04',
                       '2022-06-01',
                       '2022-07-06',
                       '2022-08-03',
                       '2022-09-07',
                       '2022-10-05',
                       '2022-11-02',
                       '2022-12-07'])
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



