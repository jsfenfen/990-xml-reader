import os
import xmltodict
import json

from .file_utils import stream_download, get_s3_URL, validate_object_id, \
    get_local_path

from .settings import KNOWN_SCHEDULES, IRS_READER_ROOT


class Filing(object):

    def __init__(self, object_id, filepath=None, URL=None):
        """ Filepath is the location of the file locally;
            URL is it's remote location (if not default)
            Ignore these and defaults will be used.
            If filepath is set, URL is ignored.
        """
        self.raw_irs_dict = None        # The parsed xml will go here
        self.version_string = None      # Version number here

        self.object_id = validate_object_id(object_id)
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
                        "File already available at %s -- skipping "
                        % self.filepath
                    )
                return False
        stream_download(self.URL, self.filepath, verbose=verbose)

    def _set_dict_from_xml(self):
        with open(self.filepath, 'r') as fh:
            raw_file = fh.read()
            self.raw_irs_dict = xmltodict.parse(raw_file)

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

    def process(self, verbose=False):
        self._download(verbose=verbose)
        self._set_dict_from_xml()
        self._set_version()
        self._set_ein()
        self._set_schedules()
