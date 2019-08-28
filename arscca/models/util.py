import os
import pdb
import requests

class Util:

    SLACK_HOOK_ENV_KEY = 'ARSCCA_SLACK_HOOK'
    SLACK_HOOK = os.environ.get(SLACK_HOOK_ENV_KEY)
    DEFAULT_SLACK_USERNAME = 'arscca'

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

