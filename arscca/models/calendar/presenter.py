from arscca.models.calendar.base_event import BaseEvent
from arscca.models.calendar.default_rally_event import DefaultRallyEvent
from arscca.models.calendar.board_meeting_event import BoardMeetingEvent
from arscca.models.calendar.msr_parser import MSRParser
from datetime import date
from datetime import timedelta

class Presenter:

    LIMIT_IN_DAYS = 30

    def __init__(self, short=False):
        '''Initialize.
        If short is True, presenter only shows events LIMIT_IN_DAYS into the future'''
        self._short = short
        self._default_rally_events = []
        self._msr_events = []
        self._msr_event_dates = set()
        self._board_meeting_events = []
        self._all = []


    def sorted_future_events(self):
        '''Return a copy of the sorted, future events from all categories'''
        if not self._all:
            self._compile()
        events = list(self._all)
        if self._short:
            end_date = date.today() + timedelta(days=self.LIMIT_IN_DAYS)
            events = [event for event in events if event.date < str(end_date)]
        return events

    def _compile(self):
        '''Fetch all event types'''
        self._fetch_msr()
        self._fetch_rally()
        self._fetch_board_meeting()
        self._combine_and_sort()

    def _fetch_msr(self):
        '''Fetch events from motorsportreg'''
        parser = MSRParser()
        self._msr_events = parser.events
        for event in self._msr_events:
            self._msr_event_dates.add(event.date)

    def _fetch_rally(self):
        '''Fetch default rally events'''
        self._default_rally_events = DefaultRallyEvent.events_not_in_motorsportreg(self._msr_event_dates)

    def _fetch_board_meeting(self):
        '''Fetch board meeting events'''
        self._board_meeting_events = BoardMeetingEvent.all()

    def _combine_and_sort(self):
        '''Returns a list of all events sorted by date'''
        events = self._default_rally_events + self._msr_events + self._board_meeting_events
        future_events = []
        for event in events:
            if event.future_boolean() and event.our_region_boolean():
                future_events.append(event)
        self._all = sorted(future_events, key=BaseEvent.date_method)


if __name__ == '__main__':
    presenter = EventPresenter()
    events = presenter.sorted_future_events()
    for event in events:
        print(event.name)
        print(event.date)
        print(event.date_formatted)
        print(event.chair)
        print(event.venue)
        print(event.address)
        print(event.org)
        print(event.link)
        print('\n---\n')

