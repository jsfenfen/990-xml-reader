import sys, os
# from .dir_utils import mkdir_p

IRS_READER_ROOT = os.path.abspath(os.path.dirname(__file__))

# This is the URL to amazon's bucket, could use another synced to it
IRS_XML_HTTP_BASE = "https://s3.amazonaws.com/irs-form-990"

# The directory we put files in while we're processing them
WORKING_DIRECTORY = (os.path.join(IRS_READER_ROOT, "XML") )

# Helpful to keep these around for lookup purposes
INDEX_DIRECTORY = (os.path.join(IRS_READER_ROOT, "CSV") )

# mkdir_p([WORKING_DIRECTORY, INDEX_DIRECTORY])

KNOWN_SCHEDULES = ["IRS990", "IRS990EZ", "IRS990PF", "IRS990ScheduleA",  \
                "IRS990ScheduleB", "IRS990ScheduleC", "IRS990ScheduleD", \
                "IRS990ScheduleE", "IRS990ScheduleF", "IRS990ScheduleG", \
                "IRS990ScheduleH", "IRS990ScheduleI", "IRS990ScheduleJ", \
                "IRS990ScheduleK", "IRS990ScheduleL", "IRS990ScheduleM", \
                "IRS990ScheduleN", "IRS990ScheduleO", "IRS990ScheduleR", \
                "ReturnHeader990x"]

try:
    from .local_settings import *
except ImportError:
    print("Error importing local_settings.py")