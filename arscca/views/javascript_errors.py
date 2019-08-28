import json
import pdb
from pyramid.view import view_config
from arscca.models.util import Util


@view_config(route_name='javascript_errors',
             renderer='json')
def javascript_errors_view(request):
    data = json.loads(request.body)

    # First Line
    message = data.pop('message')
    text = f'*{message}*\n\n'

    # Next Lines
    for key in ('path', 'file_name'):
        value = data.pop(key)
        text += f'{key}: {value}\n\n'

    # Remaining Keys
    for key, value in data.items():
        text += f'{key}: {value}\n\n'

    sent = Util.post_to_slack(text, 'arscca-javascript')

    # Tell client to alert user only if slack not sent
    # Which basically means development mode
    output = {'alert_user': not sent}

    return output
