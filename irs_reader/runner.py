from .filing import Filing
from .standardizer import Standardizer
from .sked_dict_reader import SkedDictReader
from .log_utils import configure_logging

from .settings import WORKING_DIRECTORY, ALLOWED_VERSIONSTRINGS

class Runner(object):
    """ Persist a Standardizer while processing multiple filings 
        Probably needs a better name. Logging in progress
    """
    def __init__(self):
        self.standardizer = Standardizer()
        self.group_dicts = self.standardizer.get_groups()
        self.logging = configure_logging("BulkRunner")
        self.whole_filing_data = []

    def run_filing(self, object_id):
        self.whole_filing_data = []
        this_filing = Filing(object_id)
        this_filing.process(verbose=True)
        this_version = this_filing.get_version() 
        if this_version in ALLOWED_VERSIONSTRINGS:
            this_version = this_filing.get_version()
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

                            reader = SkedDictReader(standardizer, self.group_dicts, object_id, ein,  documentId=doc_id)
                            result = reader.parse(individual_sked, parent_path=path_root)

                    else:
                        reader = SkedDictReader(standardizer, self.group_dicts, object_id, ein)
                        result = reader.parse(sked_dict, parent_path=path_root)

                else:
                    reader = SkedDictReader(self.standardizer, self.group_dicts, object_id, ein)            
                    if sked == 'ReturnHeader990x':
                        path_root = "/ReturnHeader"  
                    result = reader.parse(sked_dict, parent_path=path_root)
                self.whole_filing_data.append({'schedule_name':sked, 'data':result})
            return self.whole_filing_data
        else:            
            self.logging.info("** Skipping %s with unsupported version string %s" % (object_id, this_version) )
            return None

if __name__ == "__main__":
    from .object_ids import object_ids_2017, object_ids_2016, object_ids_2015

    TEST_DEPTH = 10
    object_ids = object_ids_2017[:TEST_DEPTH] + object_ids_2016[:TEST_DEPTH] + object_ids_2015[:TEST_DEPTH] 
    runner = Runner()
    for object_id in object_ids:
        result = runner.run_filing(object_id)
        print(result)
