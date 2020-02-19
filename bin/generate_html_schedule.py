from bs4 import BeautifulSoup
from datetime import datetime
from jinja2 import Template
from unittest import TestCase
import pdb
import requests

class MSEvent:
    '''Class that represents a single event parsed from motorsportreg'''

    BASE_URL = 'https://www.motorsportreg.com'

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




class MSParser:
    '''Class for parsing events from motorportreg and turning them into html'''
    TODAY = datetime.today()

    def __init__(self, url):
        '''Initialize'''
        self.url = url
        self.events = []

    def generate(self):
        '''Loads events and generates html'''
        self._load_events()
        return Renderer.render(self._context_to_render)

    @property
    def _context_to_render(self):
        return dict(events=self.events,
                    today=self.TODAY.strftime('%b %d, %Y'),)

    def _load_events(self):
        req = requests.get(self.url, timeout=10, headers={'User-Agent': 'arscca.org'})
        soup = BeautifulSoup(req.text, 'lxml')
        for row in soup.find_all('tr', attrs=dict(itemtype='http://schema.org/Event')):
            event = MSEvent(row)
            self.events.append(event)


class Renderer:
    TEMPLATE = Template('''
    <h2>2020 ARSCCA Schedule of Events  as of {{ today }}.</h2>
    <b>ALL EVENT DATES ARE SUBJECT TO CHANGE, so please check back regularly for updates.</b>



    <div>PLEASE NOTE:  All events listed below are Arkansas Region
         events unless denoted with *.
    </div>
    <table>
        <tr>
            <th>Date</th>
            <th>Event</th>
            <th>Location</th>
            <th>Information</th>
        </tr>
        {% for event in events %}
            <tr>
                <td>{{ event.date  }}</td>
                <td><a href='' >{{ event.name  }}</a></td>
                <td>{{ event.venue }}</td>
                <td>{{ event.link  }}</td>
                <td>{{ event.org   }}</td>
            </tr>
        {% endfor %}
    ''')


    @classmethod
    def render(cls, context):
        return cls.TEMPLATE.render(context)





class TestMSEvent(TestCase):
    HTML = '''
        <tr itemscope="itemscope" itemtype="http://schema.org/Event">
            <td>
            <div class="calendar-date">
            <div class="span12" title="Saturday, March 7, 2020">
            <div class="badge-date badge-top" content="2020-03-07" itemprop="startDate">Mar</div>
            <div class="badge-date badge-numbers" content="2020-03-07" itemprop="endDate">7</div>
            <div class="badge-date badge-bottom badge-days-weekend">S</div>
            </div>
            </div>
            </td>
            <td>
            <div class="calendar-event">
            <h3 class="title"><a href="/events/arscca-solo-ii-tnt1-snap-crackle-pop-war-memorial-stadium-scca-arkansas-473966" itemprop="url"><span itemprop="name">ARSCCA Solo II TNT1.  Snap, Crackle, Pop</span></a></h3>
            <div class="org muted">SCCA - Arkansas Region  (ARSCCA)</div>
            </div>
            <div class="calendar-place" itemprop="location" itemscope="itemscope" itemtype="http://schema.org/Place">
            <div class="venue" itemprop="name">War Memorial Stadium</div>
            <div class="address muted" itemprop="address" itemscope="itemscope" itemtype="http://schema.org/PostalAddress"><span itemprop="addressLocality">Little Rock</span>, <span itemprop="addressRegion">Arkansas</span></div>
            </div>
            </td>
        </tr>>


        '''

    SOUP = BeautifulSoup(HTML, 'lxml')

    def test_date(self):

        event = MSEvent(self.SOUP)
        assert event.date == '2020-03-07'

    def test_venue(self):

        event = MSEvent(self.SOUP)
        assert event.venue == 'War Memorial Stadium'

    def test_address(self):
        event = MSEvent(self.SOUP)
        assert event.address == 'Little Rock, Arkansas'

    def test_name(self):
        event = MSEvent(self.SOUP)
        assert event.name == 'ARSCCA Solo II TNT1.  Snap, Crackle, Pop'

    def test_org(self):
        event = MSEvent(self.SOUP)
        assert event.org == 'SCCA - Arkansas Region  (ARSCCA)'

    def test_link(self):
        event = MSEvent(self.SOUP)
        assert event.link == 'https://www.motorsportreg.com/events/arscca-solo-ii-tnt1-snap-crackle-pop-war-memorial-stadium-scca-arkansas-473966'




if __name__ == '__main__':
    parser = MSParser('https://www.motorsportreg.com/calendar/?country=US&radius=120&lat=34.80&lng=-92.24&loc=North+Little+Rock%2C+AR')
    html = parser.generate()
    print(html)





