

'''
1. Open motorsportreg.com in a browser
2. Click *Organizers*
3. Log in
4. Click Settings
5. Click Classes
6. Open Dev tools and copy the outer html for the table with class='spreadsheet dndorder'
7. Paste that content into /tmp/classes.html
8. Run this module as a script
9. Copy the output. (The output is javascript source code)
10. Paste the output into the console tab of browser developer options
11. Refresh the page to verify that it applied the sorting
'''


import json
import pdb

from bs4 import BeautifulSoup


class Sorter:

    SOURCE_FILE = '/tmp/classes.html'
    URL = '//www.motorsportreg.com/em360/index.cfm/event/profile.classes.reorder'

    __slots__ = 'html', 'klasses', 'page'

    def __init__(self):
        with open(self.SOURCE_FILE, 'r') as ff:
            self.html = ff.read()
        self.page = BeautifulSoup(self.html, 'html.parser')
        self.klasses = None

    def parse(self):
        # Reset self.klasses so this method is idempotent
        self.klasses = []
        for tr in self.page('tr'):
            # format of tr_id is srt_<uuid>
            tr_id = tr.get('id')
            if tr_id is None:
                continue
            # Format of
            uuid = tr_id[4:]
            tds = tr('td')
            abbrev = tds[1].text
            name = tds[2].text
            self.klasses.append((abbrev, name, uuid))
        self.klasses.sort()

    def _uid_classes_sorted_by_abbrev(self):
        uuids = [klass[2] for klass in self.klasses]
        return uuids

    def print(self):
        print(self.klasses)

    def print_request(self):
        '''
        This adapted from the motorsportreg page
        '''

        output = f'''

           $.post('{self.URL}',
                  {{ uidClasses: '{ ','.join(self._uid_classes_sorted_by_abbrev()) }' }},
                  function(data){{
                    console.log(data)
                  }})
        '''


        print(output)

    def save(self):
        with open('archive/classes.txt', 'w') as ff:
            ff.write(json.dumps(self.uuids))


if __name__ == '__main__':
    sorter = Sorter()
    sorter.parse()
    sorter.print_request()


