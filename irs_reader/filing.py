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
        self.json_dict = None # The parsed xml will go here
        self.version_string = None  #Version number here

        self.object_id = validate_object_id(object_id)
        if filepath:
            self.filepath = filepath
        else:
            self.filepath = get_local_path(self.object_id)

            if URL:
                self.URL = URL
            else:
                self.URL = get_s3_URL(self.object_id)

    def _download(self, force_overwrite=False,verbose=False):
        """ 
        Download the file if it's not already there.
        We shouldn't *need* to overwrite; the xml is not supposed to update.
        """ 
        if not force_overwrite:
            # If the file is already there, we're done
            if os.path.isfile(self.filepath):
                if verbose:
                    print("File already available at %s -- skipping " % self.filepath)
                return False
        stream_download(self.URL, self.filepath, verbose=verbose)

    def _set_json_from_xml(self):
        with open(self.filepath, 'r') as fh:
            raw_file=fh.read()
            self.json_dict =  xmltodict.parse(raw_file) 

    def _set_version(self):
        self.version_string = self.json_dict['Return']['@returnVersion']

    def _set_schedules(self):
        """ Attach the known and unknown schedules """
        self.schedules = []
        self.otherforms = []
        for sked in self.json_dict['Return']['ReturnData'].keys():
            if not sked.startswith("@"):
                if sked in KNOWN_SCHEDULES:
                    self.schedules.append(sked)
                else:
                    self.otherforms.append(sked)

    def get_schedule(self, skedname):
        if schedule == 'ReturnHeader990x':
            return self.json_dict['Return']['ReturnHeader']
        elif schedule in self.schedules:
            return self.json_dict['Return']['ReturnData'][schedule]
        else:
            return None

    def get_otherform(self, skedname):
        if schedule in self.otherforms:
            return self.json_dict['Return']['ReturnData'][schedule]
        else:
            return None

    def get_filepath(self):
        return self.filepath

    def get_version(self):
        return self.version_string

    def get_json(self):
        return self.json_dict
        
    def process(self, verbose=False):
        self._download()
        self._set_json_from_xml()
        self._set_version()
        self._set_schedules()


if __name__ == '__main__':
    ## 
    a = Filing(201642229349300909)
    a.process()

    print("filepath: %s version %s" % (a.get_filepath(), a.get_version()) )
    a._set_schedules()

    ## 
    filename = "%s_public.xml" % ('201642229349300909')
    a = Filing(201642229349300909, os.path.join(IRS_READER_ROOT, "XML", filename) )

    a.process()

    print("filepath: %s version %s" % (a.get_filepath(), a.get_version()) )


