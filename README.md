# irsx
### Turn the IRS' versioned XML 990's into python objects aware of the version-specific line number, description and data type 

This is a python library and command line tool to simplify working with nonprofit tax returns [released](https://aws.amazon.com/public-datasets/irs-990/) by the IRS in XML format. The library currently standarizes returns submitted in formats dating from 2013 and forwards into consistently named datastructures that follow the same format as the "paper" 990. Repeating elements, such as the salary disclosed for best compensated employees, appear at the end of each schedule.

## Installation

#### Will be easier once we put this on pypi
 
- git clone the repo 
- install locally using `$ pip install . ` from the directory with setup.py in it. It's painfully slow. You should now be able to run it as a command line utility, i.e. $ irsx --help or $ irsx_index --help
- To uninstall use `$ pip uninstall irsx`
- To see if it's installed, run `$ pip freeze`; if you see a line line 'irsx==0.0.1' it is installed. 


### About the data

The IRS releases one xml file per 990 filing, which is identified by a unique object id. Irsx uses that unique id as well, so we need to know it to extract data. To find the object\_id, look at the annual index files from the IRS (also have a look at irsx_index, a helper command described below).

The files are available at: [https://s3.amazonaws.com/irs-form-990/index_2017.csv](https://s3.amazonaws.com/irs-form-990/index_2017.csv). Other years, from 2011 forward, are available at similar URLs, just replace '2017' with the year you want [Note that the year is the year the return was received by the IRS]. Some years have >300,000 filings in them, so the index files might not open in older versions of excel.

You can use command line tools, like [csvkit](https://csvkit.readthedocs.io/en/1.0.2/), to search through the file pretty quickly to find the id you want. These are the headers:

	$ head -n 1 index_2016.csv 
	RETURN_ID,FILING_TYPE,EIN,TAX_PERIOD,SUB_DATE,TAXPAYER_NAME,RETURN_TYPE,DLN,OBJECT_ID

Using csvcut we can just spit out the EIN, TAX\_PERIOD, TAXPAYER\_NAME and the OBJECT\_ID we need by identifying the column numbers 

		$ csvcut -c 3,4,6,9 index_2016.csv | head -n 3
	EIN,TAX_PERIOD,TAXPAYER_NAME,OBJECT_ID
	742661023,201412,HARRIET AND HARMON KELLEY FOUNDATION FOR THE ARTS,201543159349100344
	562629114,201412,BROWN COMMUNITY DEVELOPMENT CORPORATION,201543109349200219


I'm looking for filings from "Sutter Health" (though note I use all caps to search). 

		$ csvcut -c 3,4,6,9 index_2016.csv | grep 'SUTTER HEALTH'
	941156621,201412,SUTTER HEALTH SACRAMENTO SIERRA REGION,201533089349301428
	990298651,201412,SUTTER HEALTH PACIFIC,201523039349301087
	942788907,201412,SUTTER HEALTH,201543089349301429

Let's use Sutter Health Sacramento Sierra Region's 12/2014 filing, which has an object id number of 201533089349301428 [ and an EIN of 941156621]. You can find the relevant filing via nonprofit explorer [here](https://projects.propublica.org/nonprofits/organizations/941156621). 

## irsx -- command line
Installing the library will also install the irsx command line tool, which uses the IRS' object_ids to reference a particular filing. This will just spit out a json representation of the entire filing. See more about the data format that's returned below.

	$ irsx 201533089349301428
	[{"schedule_name": "ReturnHeader990x", "data": {"schedule_parts"...

We could have saved it to a file with using the '>' to redirect the output

	$ irsx 201533089349301428 > 201533089349301428.json
		
The default format is json, but you can make it easier to read with the --format=txt switch, i.e. which makes it slightly more readable.

	$ irsx --format=txt 201533089349301428
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

