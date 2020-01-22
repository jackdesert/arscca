# This module fetches all published events
# so that the event name will be stored in redis

from arscca.models.published_event import PublishedEvent

import requests
#HOST = 'http://localhost:6543'
HOST = 'http://arscca.jackdesert.com'

for year, events in PublishedEvent.dates_by_year().items():
    for date, joomla_id, _, __ in events:
        url = f'{HOST}/events/{date}?cb=1'
        print(f'Parsing {date}')

        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            print(f'ERROR: {url}')

print('FINISHED!')

