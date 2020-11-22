from datetime import datetime
from datetime import date as datetime_date
import pdb
import re

class BaseEvent:
    '''Superclass for all calendar events
    Note this class is just placeholder so that if anything is undefined,
    it return an empty string
    TODO: Consider metaprogramming'''
    DATE_REGEX = re.compile(r'\d{4}-\d{2}-\d{2}')

    STANDARD_DATE_FORMAT = '%Y-%m-%d'
    FRIENDLY_DATE_FORMAT = '%b %-d, %Y'


    @property
    def chair(self):
        return ''

    def date_method(self):
        '''This method returns the same value as the *date* property but
        is callable so it can be used for sorting'''
        return self.date

    @property
    def date(self):
        return ''

    @property
    def date_formatted(self):
        '''If self.date is a date with format YYYY-MM-DD,
        returns a formatted date using FRIENDLY_DATE_FORMAT.
        Otherwise returns an empty string'''
        if self.DATE_REGEX.match(self.date):
            date_obj = datetime.strptime(self.date, self.STANDARD_DATE_FORMAT)
            return date_obj.strftime(self.FRIENDLY_DATE_FORMAT)
        return ''

    @property
    def venue(self):
        return ''

    @property
    def address(self):
        return ''

    @property
    def name(self):
        return ''

    @property
    def link(self):
        return ''

    @property
    def info(self):
        return ''

    @property
    def css_class(self):
        return ''

    def future_boolean(self):
        '''Answers the question: "Is this event in the future?"'''
        if not self.DATE_REGEX.match(self.date):
            raise AssertionError
        today = str(datetime_date.today())
        return today <= self.date

    def our_region_boolean(self):
        '''Answers the question: "Is this an ARSCCA event?"'''
        # Override in subclasses fetched from the www
        return True

