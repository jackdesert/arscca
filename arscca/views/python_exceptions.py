# See https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/views.html#custom-exception-views
from pyramid.view import view_config
from pyramid.view import exception_view_config
from pyramid.response import Response
from arscca.models.util import Util
import os
import pdb
import re
import requests
import traceback


# Only show stack frames called from our code
RELEVANT_STACKFRAME_REGEX = re.compile(r'arscca/arscca')

# Only use this view in production environment
# because in development it is more straighforward
# to see the stacktrace directly in the STDOUT
# from the server
hook_url = os.environ.get(Util.SLACK_HOOK_ENV_KEY)

if hook_url:

    @exception_view_config(Exception)
    def any_unhandled_exception(exc, request):

        exception_name = exc.__class__.__name__

        frames = traceback.extract_tb(exc.__traceback__)
        relevant_frames = []
        for frame in frames:
            if RELEVANT_STACKFRAME_REGEX.search(str(frame)):
                relevant_frames.append(frame)
        traceback_string = '\n'.join(traceback.format_list(relevant_frames))

        path   = request.environ.get('PATH_INFO')
        method = request.environ.get('REQUEST_METHOD')

        # Asterisks are like <b></b>
        text = f'*{exc.__repr__()}*\n\n*path:* {method} {path}\n\n{traceback_string}'

        payload = {'text': text,
                   'username': 'arscca-pyramid',
                   'icon_emoji': ':ghost:'}

        requests.post(hook_url, json=payload, timeout=1)

        return Response(status_int=500,
                        content_type=request.content_type,
                        json_body=dict(error='Internal Server Error'))



@view_config(route_name='exception',
     renderer='json')
def exception_view(request):
    # Use this method to verify that your slack notifier is working
    # This will raise an exception
    1 / 0
