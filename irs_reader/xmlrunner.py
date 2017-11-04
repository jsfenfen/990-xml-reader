from .filing import Filing
from .standardizer import Standardizer, Documentizer, VersionDocumentizer
from .sked_dict_reader import SkedDictReader
# from .log_utils import configure_logging
from .type_utils import listType

from .settings import WORKING_DIRECTORY, ALLOWED_VERSIONSTRINGS, CSV_ALLOWED_VERSIONSTRINGS

class XMLRunner(object):
    """ Load a Standardizer just once while running multiple filings
        Return Filing objects with results, keyerrors set
    """
    def __init__(self, documentation=False, standardizer=None, csv_format=False):
        self.documentation = documentation
        self.csv_format = csv_format

        if documentation:
            if not standardizer:    
                self.standardizer = Documentizer()
        else:
            if standardizer:
                self.standardizer = standardizer
            else:
                self.standardizer = Standardizer()
        self.group_dicts = self.standardizer.get_groups()
        self.whole_filing_data = []
        self.filing_keyerr_data = []

    def get_standardizer(self):
        return self.standardizer

    def _run_schedule_k(self, sked, object_id, sked_dict, path_root, ein):
        assert sked == 'IRS990ScheduleK'
        if type(sked_dict) == listType:
            for individual_sked in sked_dict:
                doc_id = individual_sked['@documentId']
                reader = SkedDictReader(
                    self.standardizer,
                    self.group_dicts,
                    object_id,
                    ein,
                    documentId=doc_id,
                    documentation=self.documentation,
                    csv_format=self.csv_format,
                )

                result = reader.parse(individual_sked, parent_path=path_root)
                self.whole_filing_data.append({
                    'schedule_name': sked,
                    'groups': result['groups'],
                    'schedule_parts': result['schedule_parts'],
                    'csv_line_array':result['csv_line_array']

                })
        else:
            reader = SkedDictReader(
                self.standardizer,
                self.group_dicts,
                object_id,
                ein,
                documentation=self.documentation,
                csv_format=self.csv_format,
            )

            result = reader.parse(sked_dict, parent_path=path_root)
            self.whole_filing_data.append({
                'schedule_name': sked,
                'groups': result['groups'],
                'schedule_parts': result['schedule_parts'],
                'csv_line_array':result['csv_line_array']
            })

    def _run_schedule(self, sked, object_id, sked_dict, ein):
        path_root = "/" + sked
        # Only sked K (bonds) is allowed to repeat
        if sked == 'IRS990ScheduleK':
            self._run_schedule_k(sked, object_id, sked_dict, path_root, ein)

        else:
            reader = SkedDictReader(
                self.standardizer,
                self.group_dicts,
                object_id,
                ein,
                documentation=self.documentation,
                csv_format=self.csv_format,
            )
            if sked == 'ReturnHeader990x':
                path_root = "/ReturnHeader"
            result = reader.parse(sked_dict, parent_path=path_root)

            self.whole_filing_data.append({
                'schedule_name': sked,
                'groups': result['groups'],
                'schedule_parts': result['schedule_parts'],
                'csv_line_array':result['csv_line_array']

            })

            if len(result['group_keyerrors']) > 0 or len(result['keyerrors'])> 0:
                self.filing_keyerr_data.append({
                    'schedule_name': sked,
                    'group_keyerrors':result['group_keyerrors'],
                    'keyerrors':result['keyerrors'],
                })

    def run_filing(self, object_id, verbose=False):
        self.whole_filing_data = []
        self.filing_keyerr_data = []
        this_filing = Filing(object_id)
        this_filing.process(verbose=verbose)
        this_version = this_filing.get_version()
        if verbose:
            print("Filing %s is version %s" % (object_id, this_version))
        if this_version in ALLOWED_VERSIONSTRINGS or ( self.csv_format and this_version in CSV_ALLOWED_VERSIONSTRINGS ):
            this_version = this_filing.get_version()
            schedules = this_filing.list_schedules()
            ein = this_filing.get_ein()
            self.whole_filing_data = []
            for sked in schedules:
                sked_dict = this_filing.get_schedule(sked)
                self._run_schedule(sked, object_id, sked_dict, ein)

            this_filing.set_result(self.whole_filing_data)
            this_filing.set_keyerrors(self.filing_keyerr_data)
            if verbose and not self.csv_format:   # csv format works on years with many, many keyerrors, 
                if len(self.filing_keyerr_data)>0:
                    print("In %s keyerrors: %s" % (object_id, self.filing_keyerr_data))
                else:
                    print("No keyerrors found")
            return this_filing
        else:
            print("Filing version %s isn't supported for this operation" % this_version )
            return this_filing

    def run_from_filing_obj(self, this_filing, verbose=False):  
        """
         Run from a pre-created filing object.
        """
        self.whole_filing_data = []
        self.filing_keyerr_data = []
        this_filing.process(verbose=verbose)
        object_id = this_filing.get_object_id()
        this_version = this_filing.get_version()
        if this_version in ALLOWED_VERSIONSTRINGS:
            this_version = this_filing.get_version()
            schedules = this_filing.list_schedules()
            ein = this_filing.get_ein()
            for sked in schedules:
                sked_dict = this_filing.get_schedule(sked)
                self._run_schedule(sked, object_id, sked_dict, ein)
            this_filing.set_result(self.whole_filing_data)
            this_filing.set_keyerrors(self.filing_keyerr_data)
            return this_filing
        else:
            return this_filing


    def run_sked(self, object_id, sked, verbose=False):
        """
        sked is the proper name of the schedule:
        IRS990, IRS990EZ, IRS990PF, IRS990ScheduleA, etc.
        """
        self.whole_filing_data = []
        self.filing_keyerr_data = []
        this_filing = Filing(object_id)
        this_filing.process(verbose=verbose)
        this_version = this_filing.get_version()
        if this_version in ALLOWED_VERSIONSTRINGS:
            this_version = this_filing.get_version()
            ein = this_filing.get_ein()
            sked_dict = this_filing.get_schedule(sked)
            self._run_schedule(sked, object_id, sked_dict, ein)

            this_filing.set_result(self.whole_filing_data)
            this_filing.set_keyerrors(self.filing_keyerr_data)
            return this_filing
        else:
            return this_filing


if __name__ == '__main__':
    import csv
    from .text_format_utils import debracket


    #test_set = ['201511319349301766', '201403179349305520', '201542189349301214', '201530449349302683', '201503159349304000', '201530419349300113', '201613209349309896', '201603549349300640', '201503289349300110', '201623209349310262', '201613509349300606', '201543589349300104', '201633519349301053', '201633579349300718', '201613199349306136', '201533139349300208', '201603149349302590', '201532299349304633', '201603179349200000', '201643199349302309', '201623169349100822', '201543169349101804', '201613139349100776', '201630679349300208', '201621349349101032']
    
    #test_set = ['201511319349301766', '201403179349305520', '201542189349301214', '201530449349302683', '201503159349304000', '201530419349300113', '201613209349309896', '201603549349300640', '201503289349300110', '201623209349310262', '201613509349300606', '201543589349300104', '201633519349301053', '201633579349300718', '201613199349306136', '201533139349300208', '201603149349302590', '201532299349304633', '201603179349200000', '201643199349302309', '201623169349100822', '201543169349101804', '201613139349100776', '201630679349300208', '201621349349101032', '201123159349301107', '201113349349300206', '201143189349307054', '201103139349300915', '201133199349100833', '201123199349203627', '201533209349304768', '201533179349307818', '201513089349301656', '201533189349300608', '201103159349304200', '201123129349301977', '201513359349100306', '201630529349200103', '201602259349201355', '201601369349200905']
    test_set = ['201403179349305520']
    vd = VersionDocumentizer()
    #object_id = '201303199349310500' # v2012v2.1
    #object_id = '201113139349301336' # 2010v3.2
    #object_id = '201533089349301428'  #multiple schedule K's
    #test_set = ['201123159349301107', '201113349349300206', '201143189349307054', '201103139349300915', '201133199349100833', '201123199349203627', '201533209349304768', '201533179349307818', '201513089349301656', '201533189349300608', '201103159349304200', '201123129349301977', '201513359349100306', '201630529349200103', '201602259349201355', '201601369349200905']
    xml_runner = XMLRunner(documentation=True, csv_format=True)

    standardizer = xml_runner.get_standardizer()

    for object_id in test_set:
        parsed_filing = xml_runner.run_filing(
                    object_id,
                    verbose=True
                )

        

        fieldnames = parsed_filing.get_csv_fieldnames()
        outfilename = '/Users/jfenton/github-whitelabel/validata/createdcsvs/' + object_id + ".csv"
        print("Saving to %s" % outfilename)
        outfile = open(outfilename, 'w') # 'wb' python 2?
        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
            delimiter=',',
            quotechar='"',
            lineterminator='\n',
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()


        results = parsed_filing.get_result()

        for result in results:
            for this_result in result['csv_line_array']:

                vardata = None
                try:
                    vardata = standardizer.get_var(this_result['xpath'])
                except KeyError:
                    pass

                if vardata:
                    this_result['variable_name'] = vardata['db_table'] + "_" + vardata['db_name']

                raw_line_num = vd.get_line_number(
                    this_result['xpath'], 
                    parsed_filing.get_version()
                )
                this_result['line_number'] =  debracket(raw_line_num)

                raw_description = vd.get_description(
                    this_result['xpath'], 
                    parsed_filing.get_version()
                )
                this_result['description'] =  debracket(raw_description)

                this_result['form'] = this_result['xpath'].split("/")[1]

                writer.writerow(this_result)

