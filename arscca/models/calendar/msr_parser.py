from arscca.models.calendar.msr_event import MSREvent
from arscca.models.calendar.default_rally_event import DefaultRallyEvent
from bs4 import BeautifulSoup
from datetime import datetime
import pdb
import requests

class MSRParser:
    '''Class for parsing events from motorportreg and turning them into html'''
    URL = 'https://www.motorsportreg.com/calendar/?country=US&radius=120&lat=34.80&lng=-92.24&loc=North+Little+Rock%2C+AR'

    def __init__(self):
        '''Initialize'''
        self._events = []
        self._load_events()

    @property
    def events(self):
        '''Returns a tuple of events'''
        return self._events

    def _load_events(self):
        req = requests.get(self.URL, timeout=10, headers={'User-Agent': 'arscca.org'})
        soup = BeautifulSoup(req.text, 'lxml')
        for row in soup.find_all('tr', attrs=dict(itemtype='http://schema.org/Event')):
            event = MSREvent(row)
            self._events.append(event)





