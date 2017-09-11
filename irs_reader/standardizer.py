import os
import sys
import collections 
import logging
from datetime import datetime

if sys.version_info >= (3, 0):
    import csv
else:
    import unicodecsv as csv 

from .settings import METADATA_DIRECTORY, KEYERROR_LOG
from .sked_dict_reader import SkedDictReader
from .type_utils import listType

class Standardizer(object):
    """
    This reads an ordered dict of the original xml into a standardized format.
    Data comes as variables and repeating structures, so reflect that
    """

    def __init__(self):
        self.groups = {}
        self.variables = {}
        # read in the metadata files, they should be validated elsewhere
        self._make_groups()
        self._make_variables()

    def _make_groups(self):
        group_filepath = os.path.join(METADATA_DIRECTORY, 'groups.csv')
        with open(group_filepath, 'r') as reader_fh:
            reader = csv.DictReader(reader_fh)
            for row in reader:
                self.groups[row['xpath']] = {'db_table':row['db_name']}

    def _make_variables(self):
        variable_filepath = os.path.join(METADATA_DIRECTORY, 'variables.csv')
        with open(variable_filepath, 'r') as variable_fh:
            reader = csv.DictReader(variable_fh)
            for row in reader:
                # do we need ordering? Or should there just be a flag for pretty print? 
                self.variables[row['xpath']] = {'db_table':row['db_table'], 'db_name':row['db_name'], 'ordering':row['ordering']}
    def get_groups(self):
        return self.groups

    def get_var(self, var_xpath, version=None):
        if version:
            raise Exception("Version checking is not implemented")
        return ( self.variables[var_xpath] )