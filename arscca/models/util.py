import os
import pdb
import re
import requests

from random import shuffle

class Util:

    SLACK_HOOK_ENV_KEY = 'ARSCCA_SLACK_HOOK'
    SLACK_HOOK = os.environ.get(SLACK_HOOK_ENV_KEY)
    DEFAULT_SLACK_USERNAME = 'arscca'
    KART_KLASS_REGEX = re.compile('\Aj')
    TRAILING_L_REGEX = re.compile('l\Z')


    @classmethod
    def range_with_skipped_values(cls, num_values, skipped_values):
        # Builds a list starting with one and counting up
        # by whole numbers, but skips skipped_values
        #
        # This is useful for displaying the event number
        # when certain events have been skipped
        for value in skipped_values:
            assert isinstance(value, int)

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
        for i in range(50):
            run_groups = cls._attempt_randomize_run_groups(data)
            difference = abs(len(run_groups[0]) - len(run_groups[1]))
            results[difference] = run_groups

        lowest_difference = min(results.keys())
        return results[lowest_difference]

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
            elif len(a) < len(b):
                group = a
            else:
                group = b
            if base in data:
                group[base] = data[base]
            ladies_klass = f'{base}l'
            if ladies_klass in data:
                group[ladies_klass] = data[ladies_klass]
        return (a, b, c)

