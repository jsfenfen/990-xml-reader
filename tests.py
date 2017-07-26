import os

from irs_reader.file_utils import validate_object_id
from irs_reader.filing import Filing
from irs_reader.settings import WORKING_DIRECTORY

FILING_2015V21 = '201642229349300909'
FILING_2015V21_skeds = [u'ReturnHeader990x', u'IRS990', u'IRS990ScheduleA', u'IRS990ScheduleB', u'IRS990ScheduleD', u'IRS990ScheduleM', u'IRS990ScheduleO']

# When set to false don't test download files that are already there. 
# Runs faster set to off! 
DOWNLOAD = False

def test_valid_object_id():   
    result = validate_object_id(FILING_2015V21)

def test_process_from_id_only():
    a = Filing(FILING_2015V21)
    a.process()
    assert a.get_version() == '2015v2.1'

def test_process_with_filepath():
    filename = "%s_public.xml" % FILING_2015V21
    filepath = os.path.join(WORKING_DIRECTORY, filename)
    a = Filing(FILING_2015V21, filepath=filepath)
    a.process()
    assert a.get_version() == '2015v2.1'

 
class TestWithDownload:
    def setUp(self):
        self.filing = Filing(FILING_2015V21)
        if os.path.isfile(self.filing.get_filepath()):
            if DOWNLOAD:
                os.remove(self.filing.get_filepath() )
 
    def tearDown(self):
        if DOWNLOAD:
            os.remove(self.filing.get_filepath() )
 
    def test_case_1(self):
        self.filing.process()
        assert self.filing.get_version() == '2015v2.1'

    def test_case_2(self):
        self.filing.process()
        f_skeds = self.filing.get_schedules()
        assert f_skeds == FILING_2015V21_skeds 
        for f_sked in f_skeds:
            self.filing.get_schedule(f_sked)
