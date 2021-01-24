import os
import pdb
import shutil

from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse
from pyramid.view import view_config

from arscca.models.msreg import Event
from arscca.models.shared import Shared



@view_config(route_name='msreg',
             renderer='templates/msreg.jinja2')
def msreg_view(request):

    try:
        event = Event()
        drivers = event.drivers
    except FileNotFoundError:
        drivers = []

    return dict(drivers=drivers)

@view_config(route_name='msreg_upload')
def msreg_upload_view(request):
    """
    See https://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/forms/file_uploads.html
    """

    export = request.POST['msreg_export']
    # name of the file
    filename = export.filename

    # contents
    input_file = export.file


    output_path = Shared.MSREG_RAW_PATH
    # First write to a temporary file to prevent incomplete files from
    # being used.

    output_path_temp = output_path + '~'

    # Finally write the data to a temporary file
    input_file.seek(0)
    with open(output_path_temp, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    # Now that fully saved, move it into place
    os.rename(output_path_temp, output_path)

    # Redirect
    return HTTPFound(location='/msreg')

@view_config(route_name='msreg_download')
def msreg_download_view(request):
    try:
        return FileResponse(Shared.MSREG_AUGMENTED_PATH)
    except FileNotFoundError:
        return dict(error=f'File not found: "{Shared.MSREG_AUGMENTED_PATH}"')



