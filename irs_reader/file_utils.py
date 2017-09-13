import re
import os
import requests

from datetime import datetime
from .settings import IRS_XML_HTTP_BASE, WORKING_DIRECTORY, INDEX_DIRECTORY

OBJECT_ID_RE = re.compile(r'20\d{16}')

# Not sure how much detail we need to go into here
OBJECT_ID_MSG = """
This appears not to be an IRS object id.
The ID should be 18 digits long and start with
the four digit year, e.g. 201642229349300909

To find the object id, see the yearly index csv files.
"""


def stream_download(url, target_path, verbose=False):
    """ Download a large file without loading it into memory. """
    response = requests.get(url, stream=True)
    handle = open(target_path, "wb")
    if verbose:
        print("Beginning streaming download of %s" % url)
        start = datetime.now()
        try:
            content_length = int(response.headers['Content-Length'])
            content_MB = content_length/1048576.0
            print("Total file size: %.2f MB" % content_MB)
        except KeyError:
            pass      # allow Content-Length to be missing
    for chunk in response.iter_content(chunk_size=512):
        if chunk:     # filter out keep-alive new chunks
            handle.write(chunk)
    if verbose:
        print(
            "Download completed to %s in %s" %
            (target_path, datetime.now() - start))


def validate_object_id(object_id):
    """ It's easy to make a mistake entering these, validate the format """
    result = re.match(OBJECT_ID_RE, str(object_id))
    if not result:
        print("'%s' appears not to be a valid 990 object_id" % object_id)
        raise RuntimeError(OBJECT_ID_MSG)
    return object_id


def get_s3_URL(object_id):
    return ("%s/%s_public.xml" % (IRS_XML_HTTP_BASE, object_id))


def get_local_path(object_id):
    file_name = "%s_public.xml" % object_id
    return os.path.join(WORKING_DIRECTORY, file_name)


def get_index_file_URL(year):
    return ("%s/index_%s.csv" % (IRS_XML_HTTP_BASE, year))


def get_local_index_path(year):
    csv_file_name = "index_%s.csv" % year
    return os.path.join(INDEX_DIRECTORY, csv_file_name)
