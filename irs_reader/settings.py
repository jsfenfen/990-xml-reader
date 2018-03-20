import sys
import os
from .dir_utils import mkdir_p

IRS_READER_ROOT = os.path.abspath(os.path.dirname(__file__))

# This is the URL to amazon's bucket, could use another synced to it
IRS_XML_HTTP_BASE = "https://s3.amazonaws.com/irs-form-990"

# The directory we put files in while we're processing them
WORKING_DIRECTORY = (os.path.join(IRS_READER_ROOT, "XML"))
# It can be hard to locate this.
IRSX_SETTINGS_LOCATION = (os.path.join(IRS_READER_ROOT, "settings.py"))
# Helpful to keep these around for lookup purposes
INDEX_DIRECTORY = (os.path.join(IRS_READER_ROOT, "CSV"))

KNOWN_SCHEDULES = [
                "IRS990", "IRS990EZ", "IRS990PF", "IRS990ScheduleA",
                "IRS990ScheduleB", "IRS990ScheduleC", "IRS990ScheduleD",
                "IRS990ScheduleE", "IRS990ScheduleF", "IRS990ScheduleG",
                "IRS990ScheduleH", "IRS990ScheduleI", "IRS990ScheduleJ",
                "IRS990ScheduleK", "IRS990ScheduleL", "IRS990ScheduleM",
                "IRS990ScheduleN", "IRS990ScheduleO", "IRS990ScheduleR",
                "ReturnHeader990x"
]

ALLOWED_VERSIONSTRINGS = [
    '2013v3.0', '2013v3.1', '2013v4.0', '2014v5.0', '2014v6.0',
    '2015v2.0', '2015v2.1', '2015v3.0', '2016v3.0', '2016v3.1',
]

CSV_ALLOWED_VERSIONSTRINGS = ALLOWED_VERSIONSTRINGS + [
    '2010v3.2', '2010v3.4', '2010v3.6', '2010v3.7', '2011v1.2', '2011v1.3',
    '2011v1.4', '2011v1.5', '2012v2.0', '2012v2.1', '2012v2.2', '2012v2.3', 
    '2012v3.0'
]

METADATA_DIRECTORY = (os.path.join(IRS_READER_ROOT, "metadata"))

KEYERROR_LOG = os.path.join(IRS_READER_ROOT, "keyerrors.log")
LOG_KEY = 'xml'

mkdir_p([WORKING_DIRECTORY, INDEX_DIRECTORY])

try:
    from .local_settings import *
except ImportError:
    pass