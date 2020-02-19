from bs4 import BeautifulSoup
from arscca.models.calendar.msr_event import MSREvent
from unittest import TestCase

class TestMSREvent(TestCase):
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

        event = MSREvent(self.SOUP)
        assert event.date == '2020-03-07'

    def test_venue(self):

        event = MSREvent(self.SOUP)
        assert event.venue == 'War Memorial Stadium'

    def test_address(self):
        event = MSREvent(self.SOUP)
        assert event.address == 'Little Rock, Arkansas'

    def test_name(self):
        event = MSREvent(self.SOUP)
        assert event.name == 'ARSCCA Solo II TNT1.  Snap, Crackle, Pop'

    def test_org(self):
        event = MSREvent(self.SOUP)
        assert event.org == 'SCCA - Arkansas Region  (ARSCCA)'

    def test_link(self):
        event = MSREvent(self.SOUP)
        assert event.link == 'https://www.motorsportreg.com/events/arscca-solo-ii-tnt1-snap-crackle-pop-war-memorial-stadium-scca-arkansas-473966'
