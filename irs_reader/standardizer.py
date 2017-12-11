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
    This reads metadata .csv files, which it uses to standardize
    ordered dicts. For documentation, see Documentizer below. 
    """

    def __init__(self):
        #self.show_documentation = documentation
        self.groups = {}
        self.variables = {}
        self.schedule_parts = {}

        # This is overridden for Documentizer class below
        self.variable_columns =['db_table', 'db_name']

        self._make_groups()
        self._make_variables()


    def _make_groups(self):
        group_filepath = os.path.join(METADATA_DIRECTORY, 'groups.csv')
        with open(group_filepath, 'r') as reader_fh:
            reader = csv.DictReader(reader_fh)
            for row in reader:
                self.groups[row['xpath']] = row
        return True

    def _make_variables(self):
        variable_filepath = os.path.join(METADATA_DIRECTORY, 'variables.csv')
        with open(variable_filepath, 'r') as variable_fh:
            reader = csv.DictReader(variable_fh)
            for row in reader:
                vardict = {}
                for col in self.variable_columns:
                    vardict[col]=row[col]
                self.variables[row['xpath']] = vardict


        return True

    def get_groups(self):
        return self.groups

    def get_var(self, var_xpath, version=None):
        if version:
            raise Exception("Version checking is not implemented")
        return (self.variables[var_xpath])

    def get_documentation_status(self):
        return False


class Documentizer(Standardizer):
    """ Like Standardizer, but returns canonical documentation info from 2016 version """

    def __init__(self, versions=False):
        self.groups = {}
        self.variables = {}
        self.schedule_parts = {}

        self.variable_columns =[
            'db_table', 'db_name', 'ordering', 
            'line_number', 'description', 'db_type',
            'irs_type', 'xpath'
        ]
        if versions:
            self.variable_columns = self.variable_columns + ['versions']

        self._make_schedule_parts()
        self._make_groups()
        self._make_variables()

    def get_documentation_status(self):
        return True

    def _make_schedule_parts(self):
        part_filepath = os.path.join(METADATA_DIRECTORY, 'schedule_parts.csv')
        with open(part_filepath, 'r') as reader_fh:
            reader = csv.DictReader(reader_fh)
            for row in reader:
                self.schedule_parts[row['parent_sked_part']] = {
                    'name': row['part_name'],
                    'ordering': row['ordering'],
                    'parent_sked': row['parent_sked'],
                    'parent_sked_part': row['parent_sked_part'],
                    'is_shell': row['is_shell']

                }
        return True

    def get_schedule_parts(self):
        return self.schedule_parts

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

    def get_groups_by_sked(self, sked):
        groups = []
        for thisgroup in self.groups.keys():
            if self.groups[thisgroup]['parent_sked'] == sked:
                groups.append(self.groups[thisgroup])
        return groups

    def get_parts_by_sked(self, sked):
        parts = []
        for thispart in self.schedule_parts.keys():
            #print(self.schedule_parts[thispart])
            if self.schedule_parts[thispart]['parent_sked'] == sked:
                parts.append(self.schedule_parts[thispart])
        return parts

    def get_variables(self):
        return self.variables



class VersionDocumentizer(object):
    """
    Returns version-specific line number and documentation.
    """

    def __init__(self):
        self.line_numbers = {}
        self.descriptions = {}


        self._make_line_numbers()
        self._make_descriptions()


    def _make_line_numbers(self):
        filepath = os.path.join(METADATA_DIRECTORY, 'line_numbers.csv')
        with open(filepath, 'r') as reader_fh:
            reader = csv.DictReader(reader_fh)

            for row in reader:
                try:
                    self.line_numbers[row['xpath']]
                    self.line_numbers[row['xpath']].append(row)

                except KeyError:
                    self.line_numbers[row['xpath']] = [row]

    def _make_descriptions(self):
        filepath = os.path.join(METADATA_DIRECTORY, 'descriptions.csv')
        with open(filepath, 'r') as reader_fh:
            reader = csv.DictReader(reader_fh)

            for row in reader:
                try:
                    self.descriptions[row['xpath']]
                    self.descriptions[row['xpath']].append(row)

                except KeyError:
                    self.descriptions[row['xpath']] = [row]


    def get_line_number(self, xpath, version_string):
        #print("get_line_number %s %s" % (xpath, version_string))
        if version_string == '2016v3.1':
            version_string = '2016v3.0'

        candidate_rows = []
        try:
            candidate_rows = self.line_numbers[xpath]
        except KeyError:
            return None

        for row in candidate_rows:
            if version_string in row['versions']:
                #print("get_line_number %s %s = %s" % (xpath, version_string, row['line_number']))
                return row['line_number']

        return None

    def get_description(self, xpath, version_string):
        if version_string == '2016v3.1':
            version_string = '2016v3.0'
        candidate_rows = []
        try:
            candidate_rows = self.descriptions[xpath]
        except KeyError:
            return None
        for row in candidate_rows:
            if version_string in row['versions']:
                return row['description']
        return None


        


