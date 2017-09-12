import os
from unittest import TestCase

from irs_reader.file_utils import validate_object_id
from irs_reader.filing import Filing
from irs_reader.settings import WORKING_DIRECTORY, ALLOWED_VERSIONSTRINGS
from irs_reader.standardizer import Standardizer
from irs_reader.sked_dict_reader import SkedDictReader
from irs_reader.type_utils import listType
from irs_reader.runner import Runner


# some test ids
from irs_reader .object_ids import object_ids_2017, object_ids_2016, object_ids_2015

# For running cli stuff
from irs_reader.irsx_cli import run_main as run_cli_main, get_parser as get_cli_parser
from irs_reader.irsx_index_cli import run_main as run_cli_index_main, get_parser as get_cli_index_parser


FILING_2015V21 = '201642229349300909'
FILING_2015V21_skeds = [u'ReturnHeader990x', u'IRS990', u'IRS990ScheduleA', u'IRS990ScheduleB', u'IRS990ScheduleD', u'IRS990ScheduleM', u'IRS990ScheduleO']

FILING_2014V50 = '201533089349301428' # <--  SUTTER HEALTH SACRAMENTO REGION 2014 filing has multiple schedule K's.

FILING_2014V50_skeds = ['ReturnHeader990x', 'IRS990', 'IRS990ScheduleA', 'IRS990ScheduleB', 'IRS990ScheduleC', 'IRS990ScheduleD', 'IRS990ScheduleG', 'IRS990ScheduleH', 'IRS990ScheduleI', 'IRS990ScheduleJ', 'IRS990ScheduleK', 'IRS990ScheduleL', 'IRS990ScheduleM', 'IRS990ScheduleO', 'IRS990ScheduleR']

# don't bother testing every filing in tests
TEST_DEPTH = 100

# When set to false don't test download files that are already there. 
# Runs faster set to off! 
DOWNLOAD = False

def test_valid_object_id():   
    result = validate_object_id(FILING_2015V21)

def test_process_from_id_only():
    a = Filing(FILING_2015V21)
    a.process()
    assert a.get_version() == '2015v2.1'

def test_process_from_id_only_2():
    a = Filing(FILING_2014V50)
    a.process()
    assert a.get_version() == '2014v5.0'

def test_process_with_filepath():
    filename = "%s_public.xml" % FILING_2015V21
    filepath = os.path.join(WORKING_DIRECTORY, filename)
    a = Filing(FILING_2015V21, filepath=filepath)
    a.process()
    assert a.get_version() == '2015v2.1'



class TestConversion:
    """ Still doesn't validate actual values, but... """

    def setUp(self):
        self.standardizer = Standardizer()
        self.group_dicts = self.standardizer.get_groups()

    def run_filing(self, object_id, group_dicts):
        this_filing = Filing(object_id)
        this_filing.process(verbose=False)
        this_version = this_filing.get_version() 

        if  this_version in ALLOWED_VERSIONSTRINGS:

            schedules = this_filing.list_schedules()
            ein = this_filing.get_ein()

            whole_filing_data = []

            for sked in schedules:

                sked_dict = this_filing.get_schedule(sked)
                path_root = "/" + sked

                # Only sked K is allowed to repeat
                if sked=='IRS990ScheduleK':

                    if type(sked_dict) == listType:

                        for individual_sked in sked_dict:
                            doc_id = individual_sked['@documentId']
                            
                            #self.logging.info("Handling multiple sked: %s's id=%s object_id=%s " % (sked, doc_id, object_id) )

                            reader = SkedDictReader(self.standardizer, self.group_dicts, object_id, ein,  documentId=doc_id)
                            result = reader.parse(individual_sked, parent_path=path_root)

                    else:
                        reader = SkedDictReader(self.standardizer, self.group_dicts, object_id, ein)
                        result = reader.parse(sked_dict, parent_path=path_root)

                else:
                    reader = SkedDictReader(self.standardizer, self.group_dicts, object_id, ein)            
                    if sked == 'ReturnHeader990x':
                        path_root = "/ReturnHeader"  

                    result = reader.parse(sked_dict, parent_path=path_root)

            
        else:
            print("unsupported version string %s %s" % (this_version, object_id) )
            
            #self.logging.info("** Skipping %s with unsupported version string %s" % (object_id, this_version) )


    def test_case_1(self):
        object_id = FILING_2015V21
        group_dicts = self.standardizer.get_groups()
        self.run_filing(object_id, group_dicts)

    def test_case_2(self):
        object_ids = object_ids_2017[:TEST_DEPTH] + object_ids_2016[:TEST_DEPTH] + object_ids_2015[:TEST_DEPTH] 
        group_dicts = self.standardizer.get_groups()
        for object_id in object_ids:
            self.run_filing(object_id, group_dicts)





class TestWithDownload:
    def setUp(self):
        self.filing = Filing(FILING_2015V21)
        if os.path.isfile(self.filing.get_filepath()):
            if DOWNLOAD:
                os.remove(self.filing.get_filepath() )
 
    def test_case_1(self):
        self.filing.process()
        assert self.filing.get_version() == '2015v2.1'

    def test_case_2(self):
        self.filing.process()
        f_skeds = self.filing.list_schedules()
        assert f_skeds == FILING_2015V21_skeds 
        for f_sked in f_skeds:
            self.filing.get_schedule(f_sked)


class TestCommandLine:
    def setUp(self):
        parser = get_cli_parser()
        self.parser = parser

    def test_cli_1(self):
        args = self.parser.parse_args([FILING_2015V21, '--verbose'])
        # Does it run? Output is to std out. 
        run_cli_main(args)

    def test_cli_2(self):
        # dump only main 990 in bare json format
        test_args = ['--schedule', 'IRS990', '201642229349300909']
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_3(self):
        # dump only main 990 in text format
        test_args = ['--schedule', 'IRS990', '--format', 'txt', '--documentation', '201642229349300909']
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

class TestCommandLine_Index:
    def setUp(self):
        parser = get_cli_index_parser()
        self.parser = parser
    def test_cli_index_1(self):
        args = self.parser.parse_args(['--year', '2017'])
        # Does it run? Output is to the 2017 index file.  
        if DOWNLOAD:
            run_cli_index_main(args)


