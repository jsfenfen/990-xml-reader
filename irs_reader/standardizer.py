import os
import sys
import collections
#import logging
from datetime import datetime
from .settings import METADATA_DIRECTORY, KEYERROR_LOG
from .sked_dict_reader import SkedDictReader
from .type_utils import listType
if sys.version_info >= (3, 0):
    import csv
else:
    import unicodecsv as csv


class Standardizer(object):
    """
    This reads three metadata .csv files, which it uses to standardize
    ordered dicts. Only loads documentation when needed.
    """

    def __init__(self, documentation=False):
        self.show_documentation = documentation
        self.groups = {}
        self.variables = {}
        self.schedule_parts = {}
        if self.show_documentation:
            self._make_schedule_parts()
        # read in the metadata files, they should be validated elsewhere
        self._make_groups()
        self._make_variables()

    def _make_groups(self):
        group_filepath = os.path.join(METADATA_DIRECTORY, 'groups.csv')
        with open(group_filepath, 'r') as reader_fh:
            reader = csv.DictReader(reader_fh)
            for row in reader:
                self.groups[row['xpath']] = row
        return True

    def _make_schedule_parts(self):
        part_filepath = os.path.join(METADATA_DIRECTORY, 'schedule_parts.csv')
        with open(part_filepath, 'r') as reader_fh:
            reader = csv.DictReader(reader_fh)
            for row in reader:
                self.schedule_parts[row['parent_sked_part']] = {
                    'name': row['part_name'],
                    'ordering': row['ordering']
                }
        return True

    def _make_variables(self):
        variable_filepath = os.path.join(METADATA_DIRECTORY, 'variables.csv')
        with open(variable_filepath, 'r') as variable_fh:
            reader = csv.DictReader(variable_fh)
            for row in reader:
                if self.show_documentation:
                    self.variables[row['xpath']] = {
                        'db_table': row['db_table'],
                        'db_name': row['db_name'],
                        'ordering': row['ordering'],
                        'line_number': row['line_number'],
                        'description': row['description'],
                        'db_type': row['db_type']
                    }
                else:
                    self.variables[row['xpath']] = {
                        'db_table': row['db_table'],
                        'db_name': row['db_name']
                    }
        return True

    def get_groups(self):
        return self.groups

    def part_ordering(self, partname):
        try:
            result = int(self.schedule_parts[partname]['ordering'])
            return result
        except KeyError:
            return None

    def group_ordering(self, groupname):
        try:
            return self.groups[groupname]['ordering']
        except KeyError:
            return None

    def get_documentation_status(self):
        return self.show_documentation

    def get_var(self, var_xpath, version=None):
        if version:
            raise Exception("Version checking is not implemented")
        return (self.variables[var_xpath])
