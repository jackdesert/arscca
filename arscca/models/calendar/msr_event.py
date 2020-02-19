from arscca.models.calendar.base_event import BaseEvent
from datetime import date
from jinja2 import Template
from unittest import TestCase
import pdb
import re
import requests




class MSREvent(BaseEvent):
    '''Event listed on motorsportreg'''

    BASE_URL = 'https://www.motorsportreg.com'
    REGION_NAME = 'ARSCCA'

    def __init__(self, soup):
        '''Initialize with soup'''
        self._soup = soup

    @property
    def date(self):
        return self._soup.find('div', attrs=dict(itemprop='startDate')).attrs['content']

    @property
    def venue(self):
        return self._soup.find('div', 'venue').text

    @property
    def address(self):
        return self._soup.find('div', 'address').text

    @property
    def name(self):
        return self._soup.find('h3', 'title').text

    @property
    def org(self):
        return self._soup.find('div', 'org').text

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
        return self.REGION_NAME in self.org

