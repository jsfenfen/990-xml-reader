import os
from .dir_utils import mkdir_p


IRS_READER_ROOT = "/path/to/irsreader/990-xml-reader"

# This is the URL to amazon's bucket, could use another synced to it
IRS_XML_HTTP_BASE = "https://s3.amazonaws.com/irs-form-990"

# The directory we put files in while we're processing them
WORKING_DIRECTORY = (os.path.join(IRS_READER_ROOT, "XML") )

# Helpful to keep these around for lookup purposes
INDEX_DIRECTORY = (os.path.join(IRS_READER_ROOT, "CSV") )

mkdir_p([WORKING_DIRECTORY, INDEX_DIRECTORY])