# Builtin
from collections import defaultdict
from random import shuffle
from threading import Lock
import itertools
import json
import os
import pdb
import re

# Third Party
from markdown import Markdown
import requests

class Util:

    SLACK_HOOK_ENV_KEY = 'ARSCCA_SLACK_HOOK'
    SLACK_HOOK = os.environ.get(SLACK_HOOK_ENV_KEY)
    DEFAULT_SLACK_USERNAME = 'arscca'
    KART_KLASS_REGEX = re.compile('\Aj')
    TRAILING_L_REGEX = re.compile('l\Z')
    _IP_ADDRESSES = {}

    _IP_LOCK = Lock()

    with open('config/user_passwords.json', 'r') as ff:
        __USER_PASSWORDS = json.loads(ff.read())


    @classmethod
    def range_with_skipped_values(cls, num_values, skipped_values):
        # Builds a list starting with one and counting up
        # by whole numbers, but skips skipped_values
        #
        # This is useful for displaying the event number
        # when certain events have been skipped
        for value in skipped_values:
            if not isinstance(value, int):
                raise TypeError

        output = []
        value = 1
        while len(output) < num_values:
            if value not in skipped_values:
                output.append(value)
            value += 1

        return output


    @classmethod
    def post_to_slack(cls, text, username=DEFAULT_SLACK_USERNAME):
        if not cls.SLACK_HOOK:
            print('NOT POSTING TO SLACK because no URL provided')
            return False

        payload = {'text': text,
                   'username': username,
                   'icon_emoji': ':ghost:'}

        # Using a short timeout because this is a blocking call
        requests.post(cls.SLACK_HOOK, json=payload, timeout=1)
        return True

    @classmethod
    def randomize_run_groups(cls, data):
        # input data has this format:
        # { 'CAMS': ['George', 'Leslie'],
        #   'CAMC': ['Samantha', 'Rodriguez'] }
        #
        # output is a tuple of length three with this format:
        # ([{'CAMS': ['George', 'Leslie']}],
        #  [{'CAMC': ['Samantha', 'Rodriguez']}])

        results = {}

        # Run thin N times and store in results,
        # using "difference" as the key
        for i in range(500):
            a, b, c, difference = cls._attempt_randomize_run_groups(data)
            results[difference] = (a, b, c)

        lowest_difference = min(results.keys())
        output = results[lowest_difference]

        counter = [0, 0, 0]
        for index, group in enumerate(output):
            for _, driver_names in group.items():
                counter[index] += len(driver_names)

        return output, tuple(counter)


    @classmethod
    def _attempt_randomize_run_groups(cls, data):
        a = {}
        b = {}
        c = {}
        klasses = list(data.keys())
        bases = set()
        for klass in klasses:
            base = cls.TRAILING_L_REGEX.sub('', klass)
            bases.add(base)

        bases_list = list(bases)
        shuffle(bases_list)
        for base in bases_list:
            if cls.KART_KLASS_REGEX.match(base.lower()):
                group = c
            elif cls._num_values(a) < cls._num_values(b):
                group = a
            else:
                group = b
            if base in data:
                group[base] = data[base]
            ladies_klass = f'{base}l'
            if ladies_klass in data:
                group[ladies_klass] = data[ladies_klass]
        difference = abs(cls._num_values(a) - cls._num_values(b))
        return (a, b, c, difference)

    @classmethod
    def _num_values(cls, data):
        # This function returns how many total values
        # data is expected to be a dict with lists as values
        items = itertools.chain(*data.values())
        items_list = list(items)
        return len(items_list)

    @classmethod
    def user_password_auth(cls, password):
        return password in cls.__USER_PASSWORDS


    @classmethod
    def from_arkansas(cls, request):
        ip = request.headers.get('X-Real-Ip')
        if not ip:
            # There is no such header in development mode,
            # so play nice and return True
            return True
        return cls._region_from_ip(ip) == 'Arkansas'

    @classmethod
    def _region_from_ip(cls, ip):
        # If we use the default requests' user agent,
        # we get 429 errors on every request.
        # ipapi.co verified that they use heuristics to decide
        # whether someone on the free plan is over their rate limit.
        # Specifying a custom user agent appears to clear us from
        # other IP blocks that have already used up their quotas.
        headers = {'User-Agent': 'arscca-pyramid'}
        url = f'https://ipapi.co/{ip}/json'


        # Wrap this in a lock so multiple concurrent requests
        # from the same IP address (like a web scraper)
        # will only require one API call
        with cls._IP_LOCK:
            if region := cls._IP_ADDRESSES.get(ip):
                return region


            # TODO handle timeout exceptions
            data = requests.get(url, timeout=5, headers=headers).json()
            region = data.get('region')
            cls._IP_ADDRESSES[ip] = region

        return region

    @classmethod
    def html_from_markdown(cls, markdown_string, context={}):
        '''
        A simple templating tool.
        First keys from context are substituted using jinja2-style syntax.
        ARGUMENTS:
          markdown_string: a string of markdown text
          context: a dictionary of values to substitute

        OUTPUT:
          html.

        EXAMPLE:
           >>> markdown_string = '# Hello {{ name }}'
           >>> context = dict(name='Charlie')
           >>> Util.html_from_markdown(markdown_string, context)
           '<h1>Hello Charlie</h1>'
        '''

        for key, value in context.items():
            prep_a = '\{\{\s*KEY\s*\}\}'
            prep_b = prep_a.replace('KEY', key)
            regex = re.compile(prep_b)
            markdown_string = regex.sub(value, markdown_string)

        html = Markdown().convert(markdown_string)
        return html


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    #pdb.set_trace()
    #ip = '99.99.252.41'
    #url = f'https://ipapi.co/{ip}/json'

    #data = requests.get(url, timeout=5, headers=headers).json()
    #body.json().get('region')
    #pdb.set_trace()
    #1
