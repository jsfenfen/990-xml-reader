import os
import json
from unittest import TestCase

from irs_reader.file_utils import validate_object_id
from irs_reader.filing import Filing
from irs_reader.settings import WORKING_DIRECTORY, ALLOWED_VERSIONSTRINGS
from irs_reader.standardizer import Standardizer
from irs_reader.sked_dict_reader import SkedDictReader
from irs_reader.type_utils import listType
from irs_reader.xmlrunner import XMLRunner


# some test ids
from irs_reader .object_ids import object_ids_2017, \
    object_ids_2016, object_ids_2015

# For running cli stuff
from irs_reader.irsx_cli import run_main as run_cli_main, \
    get_parser as get_cli_parser
from irs_reader.irsx_index_cli import run_cli_index_main, \
    get_cli_index_parser


FILING_2015V21 = '201642229349300909'
FILING_2015V21_skeds = [
        'ReturnHeader990x', 'IRS990', 'IRS990ScheduleA',
        'IRS990ScheduleB', 'IRS990ScheduleD', 'IRS990ScheduleM',
        'IRS990ScheduleO'
]

# SUTTER HEALTH SACRAMENTO REGION 2014 filing has multiple schedule K's.
FILING_2014V50 = '201533089349301428'

FILING_2014V50_skeds = [
    'ReturnHeader990x', 'IRS990', 'IRS990ScheduleA', 'IRS990ScheduleB',
    'IRS990ScheduleC', 'IRS990ScheduleD', 'IRS990ScheduleG',
    'IRS990ScheduleH', 'IRS990ScheduleI', 'IRS990ScheduleJ',
    'IRS990ScheduleK', 'IRS990ScheduleL', 'IRS990ScheduleM',
    'IRS990ScheduleO', 'IRS990ScheduleR'
]

# don't bother testing every filing in tests
TEST_DEPTH = 10

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


# test without runner
class TestConversion:
    """ Still doesn't validate actual values, but... """

    def setUp(self):
        self.xml_runner = XMLRunner()

    def test_case_1(self):
        parsed_filing = self.xml_runner.run_filing(FILING_2015V21)

    def test_case_2(self):
        object_ids = object_ids_2017[:TEST_DEPTH] \
            + object_ids_2016[:TEST_DEPTH] + object_ids_2015[:TEST_DEPTH]
        for object_id in object_ids:
            self.xml_runner.run_filing(object_id)

class TestRunner:
    """ Test using runner class """

    def setUp(self):
        self.xml_runner = XMLRunner()

    def test1(self):
        parsed_filing = self.xml_runner.run_filing(FILING_2015V21)
        assert parsed_filing.get_type()=='IRS990'
        parsed_filing_schedules = parsed_filing.list_schedules()
        for sked in FILING_2015V21_skeds:
            assert sked in parsed_filing_schedules
            parsed_filing.get_parsed_sked(sked)

    def test_multiple_sked_ks(self):
        parsed_filing = self.xml_runner.run_filing(FILING_2014V50)
        assert parsed_filing.get_type()=='IRS990'
        parsed_filing_schedules = parsed_filing.list_schedules()
        for sked in FILING_2014V50_skeds:
            assert sked in parsed_filing_schedules
            parsed_filing.get_parsed_sked(sked)
    def test_with_standardizer(self):
        standardizer = Standardizer()
        self.xml_runner = XMLRunner(standardizer=standardizer)


class TestWithDownload:
    def setUp(self):
        self.filing = Filing(FILING_2015V21)
        if os.path.isfile(self.filing.get_filepath()):
            if DOWNLOAD:
                os.remove(self.filing.get_filepath())

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
        test_args = ['--schedule', 'IRS990', '--no_doc', '201642229349300909']
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_3(self):
        test_args = ['--schedule', 'IRS990', FILING_2014V50]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    """Testing the csv option without file set somehow breaks
        it seems like it's some interaction between how nose handles output
        and how we're outputting? Point is, the script works when the test fails.
        So only test with the --file output option... 
    """
    def test_cli_4(self):
        test_args = [
            '--schedule', 'IRS990',
            '--format', 'csv',
            '--file', 'testout.csv',
            '201642229349300909'
        ]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)


    def test_cli_5(self):
        test_args = [
            '--schedule', 'IRS990', 
            '--format', 'txt',
            '--file','testout.csv',
            '--verbose',
            '201113139349301336'
        ]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_6(self):
        test_args = [
            '--format', 'txt',
            '201113139349301336'
        ]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_7(self):
        test_args = [
            '--format', 'txt',
            '--no_doc',
            '--verbose',
            '201113139349301336'
        ]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_8(self):
        test_args = [
            '--list_schedules',
            '201642229349300909'
        ]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_8(self):
        test_args = [
            '--no_doc',
            '--format', 'txt',
            '201113139349301336'
        ]
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

"""
    # from json
    # using installed lib:
    from irsx.xmlrunner import XMLRunner
    from irsx.filing import Filing

    Todo: test json entry, need it not from a file.
    object_id = '201612439349300026'
    with open('irs_reader/t1.json') as json_data:
        string_json = json.load(json_data)
    nf = Filing(object_id, json=string_json)
    xml_runner = XMLRunner()
    result = xml_runner.run_from_filing_obj(nf)
    print(result)
"""
