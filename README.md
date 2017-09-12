# irsx
### Turn the IRS' versioned XML 990's into python objects aware of the version-specific line number, description and data type 

This is a python library and command line tool to simplify working with nonprofit tax returns released by the IRS in XML format. 



The IRS identifies electronic filings by their object_id, available in the annual index files released [link].

## Installation

#### The directions below are a hack--we should put this on PyPI when released
 
- git clone the repo 
- install locally using `$ pip install . ` from the directory with setup.py in it. It's painfully slow. You should now be able to run it as a command line utility, i.e. $ irsx --help or $ irsx_index --help
- To uninstall use `$ pip uninstall irsx`
- To see if it's installed, run `$ pip freeze`; if you see a line line 'irsx==0.0.1' it is installed. 


## irsx -- command line
Installing the library will also install the irsx command line tool, which uses the IRS' object_ids to reference a particular filing. This will just spit out the string representation of an ordered dictionary for the entire filing. 

	$ irsx 201642229349300909
	[{"schedule_name": "ReturnHeader990x", "data": {"schedule_parts"...

We could have saved it to a file with using the '>' to redirect the output

	$ irsx 201642229349300909 > 201642229349300909.json
		
The default format is json, but you can make it easier to read with the --format=txt switch, i.e. which makes it slightly more readable.

	$ irsx --format=txt 201642229349300909
	[
	    {
	        "schedule_name": "ReturnHeader990x",
	        "data": {
	            "schedule_parts": {
	                "returnheader990x_part_i": {
	                    "object_id": 201642229349300909,
	                    "ein": "431786847",
	                    "RtrnHdr_RtrnTs": "2016-08-09T08:31:41-07:00",
	                    "RtrnHdr_TxPrdEndDt": "2015-12-31",
	                    ...
	                    
That's better, but it's still really hard to follow. Use the --documentation flag in text format to make this easier to follow: 

	$ irsx --format=txt --documentation 201642229349300909

		Schedule: ReturnHeader990x
		
		
		returnheader990x_part_i
		
		
			*ein*: value=431786847 
			Line Number '' Description: 'IRS employer id number' Type: String(9)

		
That's a more useful representation of the filing--it also appears roughly in the same order as a paper 990 filing (with the exception of repeating groups, which appear at the end of each schedule). It's also remarkably verbose.

We can narrow in on a single schedule, but first we need to know what is present in this filing, using the --list_schedules option
		 
	
		$ irsx --list_schedules 201642229349300909
	
		['ReturnHeader990x', u'IRS990', u'IRS990ScheduleA', u'IRS990ScheduleB', 
		u'IRS990ScheduleD', u'IRS990ScheduleM', u'IRS990ScheduleO']
	
Now let's look at a human readable text version of schedule M

	$ irsx --format=txt --documentation --schedule=IRS990ScheduleM 201642229349300909

		Schedule: IRS990ScheduleM
		
		
		skedm_part_i
		
		
			*ein*: value=431786847 
			Line Number '' Description: 'IRS employer id number' Type: String(9)
		
			*object_id*: value=201642229349300909 
			Line Number '' Description: '' Type: 
		
			*SkdM_AnyPrprtyThtMstBHldInd*: value=false 
			Line Number ' Part I Line 30a' Description: ' Any property that must be held?' Type: String(length=5)
		
			*SkdM_RvwPrcssUnslNCGftsInd*: value=false 
			Line Number ' Part I Line 31' Description: ' Review process reference unusual noncash gifts?' Type: String(length=5)
		
			*SkdM_ThrdPrtsUsdInd*: value=false 
			Line Number ' Part I Line 32a' Description: ' Third parties used?' Type: String(length=5)
		
			*RlEsttCmmrcl_NnCshChckbxInd*: value=X 
			Line Number ' Part I Line 16; Column (a)' Description: ' Real estate - commercial; Checkbox for lines on Part I' Type: String(length=1)
		
			*RlEsttCmmrcl_CntrbtnCnt*: value=6 
			Line Number ' Part I Line 16; Column (b)' Description: ' Real estate - commercial; Number of contributions' Type: BigInteger
		
			*RlEsttCmmrcl_NncshCntrbtnsRptF990Amt*: value=190500 
			Line Number ' Part I Line 16; Column (c)' Description: ' Real estate - commercial; Revenues reported on F990, Pt VIII, line 1g' Type: BigInteger


The "text" representation is under development and may change, though the underlying json output should not. We can save just that schedule to file with:

	$ irsx --schedule=IRS990ScheduleM 201642229349300909 > 201642229349300909.json



## irsx -- use from python

Much broader functionality is available by running from within python.


	>>> from irs_reader.runner import Runner
	>>> xml_runner = Runner()
	>>> result = xml_runner.run_filing_single_schedule(201642229349300909, 'IRS990ScheduleM')
	>>> result[0]['data']['schedule_parts']['skedm_part_i']['RlEsttCmmrcl_NncshCntrbtnsRptF990Amt']
	'190500' 



## Introduction to the IRS' MEF 990 XML

### irsx_index : Get the index files, --year[ly]

The IRS maintains annual index files, from 2011 forwards, of what filings have been received electronically and approved for release. Use the utility command, '$ irsx_index' to retrieve them all, or use the --year option to pick just one. Here we just grab 2017. Note that the --verbose flag is on, so that it'll say where the file is saved to. 

	$ irsx_index --year 2017 --verbose
	Getting index file for year: 2017
	Beginning streaming download of https://s3.amazonaws.com/irs-form-990/index_2017.csv
	Total file size: 18.18 MB
	Download completed to /Users/jfenton/github-whitelabel/envs/irsreader_env/lib/python2.7/site-packages/irs_reader/CSV/index_2017.csv in 0:00:02.934290

The location is specified in the settings file, but by default it'll go into a subdirectory of wherever the code is installed called /CSV/. You could set that by modifying the .settings file, but we'll save that for later.

 You could look at the file in a spreadsheet program, and you might want to keep it in your own database, but here I'll just use csvkit (`$ pip install csvkit`) to find something. Note that I'm doing this in the same directory as the file is in, to save typing. 
 
	cd /path/to/virtualenv/lib/python2.7/site-packages/irs_reader/CSV/
	


# Dev directions

#### To use without installing via pip

- from the directory with the readme in it, instead of the irsx command, use `$python -m python -m irs_reader.cli` or `$python -m irs_reader.cli_index` (for irsx_index) so that the command line tools are run as modules and python doesn't freak out. 


## Testing

Nosetests - Test coverage is incomplete

Tox -- see tox.ini; testing for: 2.7,3.5,3.6 . You may need to run `pip install tox` in the testing environment. 

