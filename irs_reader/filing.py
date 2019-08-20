import os
import sys
import io
import xmltodict
import json
from collections import OrderedDict
from xml.parsers.expat import ExpatError
from .type_utils import dictType, orderedDictType, listType, \
    unicodeType, noneType, strType

from .file_utils import stream_download, get_s3_URL, validate_object_id, \
    get_local_path

from .settings import KNOWN_SCHEDULES, IRS_READER_ROOT


class InvalidXMLException(Exception):
    pass


class Filing(object):

    def __init__(self, object_id, filepath=None, URL=None, json=None):
        """ Filepath is the location of the file locally;
            URL is it's remote location (if not default)
            Ignore these and defaults will be used.
            If filepath is set, URL is ignored.
            json is a json representation of the data, so if given, 
            no file will be downloaded.
        """
        self.raw_irs_dict = None        # The parsed xml will go here
        self.version_string = None      # Version number here

        self.object_id = validate_object_id(object_id)
        self.result = None
        self.processed = False
        self.keyerrors = None
        self.csv_result = None

        if json:
            self.json = json
            self.input_type = 'json'
        else:
            self.json = None
            self.input_type = 'xml'
            if filepath:
                self.filepath = filepath
            else:
                self.filepath = get_local_path(self.object_id)

                if URL:
                    self.URL = URL
                else:
                    self.URL = get_s3_URL(self.object_id)

    def _download(self, force_overwrite=False, verbose=False):
        """
        Download the file if it's not already there.
        We shouldn't *need* to overwrite; the xml is not supposed to update.
        """
        if not force_overwrite:
            # If the file is already there, we're done
            if os.path.isfile(self.filepath):
                if verbose:
                    print(
                        "File already available at %s -- skipping"
                        % (self.filepath)
                    )
                return False
        stream_download(self.URL, self.filepath, verbose=verbose)
        return True

    def _denamespacify(self,entity):
        """
        It's legal to include namespaces in the xml tags, e.g. irs:Return instead of Return
        This is very rare; see 201940149349301304_public.xml for an example.
        """
        thisentitytype = type(entity)
        if thisentitytype == orderedDictType:
            newOD = OrderedDict()
            for key in entity.keys():
                newkey = key
                if ":" in key:
                    newkey = key.split(":")[1]
                newvalue = entity[key]
                if type(newvalue) == listType or type(newvalue) == orderedDictType:
                    newvalue = self._denamespacify(newvalue)
                newOD[newkey] = newvalue
            return newOD

        elif thisentitytype == listType:
            newlist = list()
            for item in entity:
                newvalue = item
                if type(newvalue) == listType or type(newvalue) == orderedDictType:
                    newvalue = self._denamespacify(newvalue)
                newlist.append(newvalue)
            return newlist
        else: 
            return entity


    def _set_dict_from_xml(self):
        # io works across python2 and 3, and allows an encoding arg        
        with io.open(self.filepath, 'r', encoding='utf-8-sig') as fh:
            raw_file = fh.read()
            try:

                self.raw_irs_dict = self._denamespacify(xmltodict.parse(raw_file))
            except ExpatError:
                raise InvalidXMLException(
                    "\nXML Parse error in " + self.filepath \
                    + "\nFile may be damaged or incomplete.\n"\
                    + "Try erasing this file and downloading again."
                )
            try:
                self.raw_irs_dict['Return']
            except KeyError:
                raise InvalidXMLException(
                    "'Return' element not located in" + self.filepath \
                    + "\nFile may be damaged or incomplete.\n" \
                    + "Try erasing this file and downloading again."
                )



    def _set_dict_from_json(self):

        self.raw_irs_dict = self.json

    def _set_version(self):
        self.version_string = self.raw_irs_dict['Return']['@returnVersion']

    def _set_ein(self):
        self.ein = self.raw_irs_dict['Return']['ReturnHeader']['Filer']['EIN']

    def _set_schedules(self):
        """ Attach the known and unknown schedules """
        self.schedules = ['ReturnHeader990x', ]
        self.otherforms = []
        for sked in self.raw_irs_dict['Return']['ReturnData'].keys():
            if not sked.startswith("@"):
                if sked in KNOWN_SCHEDULES:
                    self.schedules.append(sked)
                else:
                    self.otherforms.append(sked)

    def get_object_id(self):
        return self.object_id

    def get_schedule(self, skedname):
        if skedname == 'ReturnHeader990x':
            return self.raw_irs_dict['Return']['ReturnHeader']
        elif skedname in self.schedules:
            return self.raw_irs_dict['Return']['ReturnData'][skedname]
        else:
            return None

    def get_ein(self):
        return self.ein

    def get_otherform(self, skedname):
        if skedname in self.otherforms:
            return self.raw_irs_dict['Return']['ReturnData'][skedname]
        else:
            return None

    def get_filepath(self):
        return self.filepath

    def get_version(self):
        return self.version_string

    def get_raw_irs_dict(self):
        return self.raw_irs_dict

    def list_schedules(self):
        return self.schedules

    def set_result(self, result):
        self.result = result

    def get_result(self):
        return self.result

    def set_csv_result(self, csv_result):
        self.csv_result = csv_result
        
    def get_csv_result(self):
        return self.csv_result

    def set_keyerrors(self, keyerrorlist):
        self.keyerrors = keyerrorlist

    def get_keyerrors(self):
        return self.keyerrors
        
    def get_unparsed_json(self):
        """ Json dicts are unordered """ 
        return json.dumps(self.raw_irs_dict)

    def get_type(self):
        if 'IRS990' in self.schedules:
            return 'IRS990'
        elif 'IRS990EZ' in self.schedules:
            return 'IRS990EZ'
        elif 'IRS990PF' in self.schedules:
            return 'IRS990PF'    
        else:
            raise Exception("Missing 990/990EZ/990PF-is this filing valid?")

    def get_parsed_sked(self, skedname):
        """ Returns an array because multiple sked K's are allowed"""
        if not self.processed:
            raise Exception("Filing must be processed to return parsed sked")
        if skedname in self.schedules:
            matching_skeds = []
            for sked in self.result:
                if sked['schedule_name']==skedname:
                    matching_skeds.append(sked)
            return matching_skeds
        else:
            return []

    def process(self, verbose=False):
        # don't reprocess inadvertently
        if not self.processed:
            self.processed=True
            if self.json:
                self._set_dict_from_json()
            else:
                self._download(verbose=verbose)
                self._set_dict_from_xml()

            self._set_version()
            self._set_ein()
            self._set_schedules()
