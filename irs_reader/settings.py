import sys
import os
from .dir_utils import mkdir_p

IRS_READER_ROOT = os.path.abspath(os.path.dirname(__file__))

# This is the URL to amazon's bucket, could use another synced to it
IRS_XML_HTTP_BASE = "https://s3.amazonaws.com/irs-form-990"

# It can be hard to locate this.
IRSX_SETTINGS_LOCATION = (os.path.join(IRS_READER_ROOT, "settings.py"))

# Defaults to the same directory as this settings file, but you can override
# with the `IRSX_CACHE_DIRECTORY` environment variable
IRSX_CACHE_DIRECTORY = os.environ.get("IRSX_CACHE_DIRECTORY", IRS_READER_ROOT)

# The directory we put files in while we're processing them
WORKING_DIRECTORY = os.environ.get(
    "IRSX_WORKING_DIRECTORY", os.path.join(IRSX_CACHE_DIRECTORY, "XML"))
# Helpful to keep these around for lookup purposes
INDEX_DIRECTORY = os.environ.get(
    "IRSX_INDEX_DIRECTORY", os.path.join(IRSX_CACHE_DIRECTORY, "CSV"))

IRS_INDEX_BASE = "https://apps.irs.gov/pub/epostcard/990/xml/%s/index_%s.csv"

KNOWN_SCHEDULES = [
                "IRS990", "IRS990EZ", "IRS990PF", "IRS990ScheduleA",
                "IRS990ScheduleB", "IRS990ScheduleC", "IRS990ScheduleD",
                "IRS990ScheduleE", "IRS990ScheduleF", "IRS990ScheduleG",
                "IRS990ScheduleH", "IRS990ScheduleI", "IRS990ScheduleJ",
                "IRS990ScheduleK", "IRS990ScheduleL", "IRS990ScheduleM",
                "IRS990ScheduleN", "IRS990ScheduleO", "IRS990ScheduleR",
                "ReturnHeader990x"
]

MIN_SUPPORTED_VERSION_YEAR = 2013


def version_is_supported(version_string):
    """Return True if a version string is >= 2013 (e.g. '2013v3.0')."""
    try:
        year = int(version_string.split('v')[0])
        return year >= MIN_SUPPORTED_VERSION_YEAR
    except (ValueError, IndexError):
        return False

METADATA_DIRECTORY = (os.path.join(IRS_READER_ROOT, "metadata"))

KEYERROR_LOG = os.path.join(IRS_READER_ROOT, "keyerrors.log")
LOG_KEY = 'xml'

mkdir_p([WORKING_DIRECTORY, INDEX_DIRECTORY])

try:
    from .local_settings import *
except ImportError:
    pass
