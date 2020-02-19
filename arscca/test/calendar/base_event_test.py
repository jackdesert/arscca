from arscca.models.calendar.board_meeting_event import BoardMeetingEvent
from arscca.models.calendar.base_event import BaseEvent
from datetime import date as datetime_date
from datetime import timedelta
from unittest import TestCase

class TestBaseEvent(TestCase):
    def test_date_formatted(self):
        '''Verify that formatted date has the expected format.
        The method we are testing is BaseEvent.date_formatted.
        Note that we are instantiating an BoardMeetingEvent,
        since the BaseEvent is not meant to be instantiated'''

        date = '2020-01-05'
        event = BoardMeetingEvent(date)
        assert event.date_formatted == 'Jan 5, 2020'

    def test_future_boolean(self):
        today     = datetime_date.today()
        yesterday = str(today - timedelta(days=1))
        tomorrow  = str(today + timedelta(days=1))

        today = str(today)



        assert BoardMeetingEvent(today).future_boolean()
        assert BoardMeetingEvent(tomorrow).future_boolean()
        assert not BoardMeetingEvent(yesterday).future_boolean()
