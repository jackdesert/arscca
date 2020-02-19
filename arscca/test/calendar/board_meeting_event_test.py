from arscca.models.calendar.board_meeting_event import BoardMeetingEvent
from datetime import date as datetime_date
from datetime import timedelta
from unittest import TestCase

class TestBoardMeetingEvent(TestCase):
    def test_all_future_events_1(self):

        events = BoardMeetingEvent.all()
        assert events
        for event in events:
            assert event.venue
            assert event.address
            assert event.date
            assert event.date_formatted

    def test_all_future_events_2(self):
        '''Verify that only future dates returned'''

        today = datetime_date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        test_dates = [str(date) for date in [today, yesterday, tomorrow]]

        events = BoardMeetingEvent.all(test_dates)
        event_dates = [event.date for event in events]
        assert event_dates == test_dates
