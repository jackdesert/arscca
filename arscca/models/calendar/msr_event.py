from datetime import date
from unittest import TestCase
import pdb
import re

from jinja2 import Template
import requests

from arscca.models.calendar.base_event import BaseEvent


class MSREvent(BaseEvent):
    '''Event listed on motorsportreg'''

    BASE_URL = 'https://www.motorsportreg.com'
    REGION_NAME = 'ARSCCA'

    #DRIVERS_MEETING_TIMES = { 5 : 'Sleep-In Saturday. Driver meeting 10:15', 6: 'Early Sunday. Driver meeting 9:15' }
    DRIVERS_MEETING_TIMES = { 5 : 'Sleepy Saturday. <b>10:15</b> Driver meeting', 6: 'Early Sunday. <b>9:15</b> Driver meeting' }

    def __init__(self, soup):
        '''Initialize with soup'''
        self._soup = soup

    @property
    def date(self):
        return self._soup.find('span', attrs=dict(itemprop='startDate')).attrs['content']

    @property
    def venue(self):
        return self._soup.find('div', attrs=dict(itemtype='http://schema.org/Place')).find('span', attrs=dict(itemprop='name')).text

    @property
    def stuttgart(self):
        if 'stuttgart' in self.venue.lower():
            return True
        return False

    @property
    def address(self):
        return self._soup.find('span', attrs=dict(itemtype='http://schema.org/PostalAddress')).text

    @property
    def name(self):
        return self._soup.find('h3', 'title').text

    @property
    def link(self):
        title = self._soup.find('h3', 'title')
        anchor = title.find('a')
        href = anchor.attrs['href']
        return f'{self.BASE_URL}{href}'

    @property
    def css_class(self):
        if 'rally' in self.name.lower():
            return 'rallyx'
        else:
            return 'autox'

    def our_region_boolean(self):
        '''Answers the question: "Is this an ARSCCA event?"'''
        return '(ARSCCA)' in self._soup.text

    @property
    def info(self):
        if 'rallyx' in self.name.lower():
            return ''
        weekday = None
        if obj := self._date_obj():
            weekday = obj.weekday()

        start_time = self.DRIVERS_MEETING_TIMES.get(weekday)
        if start_time is not None:
            return start_time
        return weekday
        return ''

