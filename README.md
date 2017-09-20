# irsx

## Table of Contents

- [Quickstart](#quickstart)
- [About](#about)
- [Installation](#installation)
- [Command line irsx](#command-line-irsx)
- [Find an object_id](#getting-an-object-id)
- [irsx_index: get yearly index files](#irsx_index) 
- [Developer directions](#developer-directions)
- [Testing](#testing)

## Quickstart
We're using the "object_id" 201533089349301428 to refer to the Dec. 2014 990 filed by "Sutter Health Sacramento Region", which is described in the [2016 index file](https://s3.amazonaws.com/irs-form-990/index_2016.csv). 

	>>> from irsx.xmlrunner import XMLRunner
	>>> xml_runner = XMLRunner()
	>>> parsed_filing = xml_runner.run_schedule(201533089349301428, 'IRS990ScheduleJ')
	>>> key_employees = parsed_filing.get_result()[0]['groups']['SkdJRltdOrgOffcrTrstKyEmpl']
	>>> for employee in key_employees:                                                                
		  print(employee['PrsnNm'])


## About

IRSX is a python library and command line tool to simplify working with nonprofit tax returns [released](https://aws.amazon.com/public-datasets/irs-990/) by the IRS in XML format. The library currently standarizes returns submitted in formats dating from 2013 and forwards into consistently named datastructures that follow the same format as the "paper" 990. Repeating elements, such as the salary disclosed for best compensated employees, appear at the end of each schedule. We plan to release updated metadata that will allow processing of earlier forms.

From the command line, xml files can be output as machine readable json, or human readable text, optionally with documentation. From within a python program, the results are returned as native data structures. 

The tax returns are complex--the easiest way to understand them is to consult the [metadata csv files](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/metadata), and cross reference these to the forms in [sample\_schedules](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/sample_schedules) (which contains recent pdf versions of the schedules).  The data returned for each schedule read contains schedule parts (see the [schedule\_parts.csv](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/metadata/schedule_parts.csv) for all possible parts) and repeating groups (see [groups.csv](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/metadata/groups.csv)) that occur within that schedule. Both repeating groups and schedule\_parts contain variables, which are documented in the [variables.csv](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/metadata/variables.csv) table. 





## Installation

#### Will be easier once we put this on pypi
 
- git clone the repo 
- install locally using `$ pip install . ` from the directory with setup.py in it. It's painfully slow. You should now be able to run it as a command line utility, i.e. $ irsx --help or $ irsx_index --help
- To uninstall use `$ pip uninstall irsx`
- To see if it's installed, run `$ pip freeze`; if you see a line line 'irsx==0.0.1' it is installed. 


## command line irsx
Installing the library will also install the irsx command line tool, which uses the IRS' object_ids to reference a particular filing. This will just spit out a json representation of the entire filing. See more about how to get an IRS object_id and how to read the data format that's returned below.

	$ irsx 201533089349301428
	[{"schedule_name": "ReturnHeader990x", "groups": {}, "schedule_parts": {"returnheader990x_part_i": {"object_id": 201533089349301428, "ein": "941156621", "RtrnHdr_RtrnTs": "2015-11-04T20:09:01-06:00",...


The general structure of the return is an array of schedules:

	[
	      {
	        "schedule_name": <Schedule Name>,
	        "schedule_parts": {
	                "<schedule_part name>": { dictionary of variables in this part },
	                	...
	        "groups": {
	        	"<group name>":
	        		[ Array of groups of this name that were found
	        			{ dictionary of variables in this group }
	        		]
	        }, ... 
	]
	        
	
Each schedule part or repeating group includes the original object\_id and ein of the filing as well as all the IRS variables. The schedule\_part name and the group name are the values that appear in those respective .csv files in the [metadata directory](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/metadata). If a particular schedule, schedule part or repeating group has no values, it is not included.

Note that IRSX will download the file if it hasn't already--for more information about the location, use the --verbose option. IRSX by default will retrieve the file from the IRS' public Amazon S3 bucket. If you plan to work with a large collection of files, you may want to host xml on your own bucket, and use bulk tools like AWS CLI's sync to move many documents at once.


We could have saved it to a file with using the '>' to redirect the output

	$ irsx 201533089349301428 > 201533089349301428.json
		
The default format is json, but you can make it easier to read with the --format=txt switch. The whole output is much longer, I've truncated here.

	$ irsx --format=txt 201533089349301428
	[
      {
        "schedule_name": "ReturnHeader990x",
        "data": {
            "schedule_parts": {
                "returnheader990x_part_i": {
                    "object_id": 201533089349301428,
	                    ...
	           	"part_i

	                    
That's better, but it's still really hard to follow. Use the --documentation flag in text format to make this easier to follow: 

	$ irsx --format=txt --documentation 201533089349301428

	Schedule: ReturnHeader990x
	
	
	returnheader990x_part_i
	
	
		*ein*: value=941156621 
		Line Number 'NA' Description: 'IRS employer id number' Type: String(9)
	
		*object_id*: value=201533089349301428 
		Line Number 'NA' Description: 'IRS-assigned object id' Type: String(18)
	
		*RtrnHdr_RtrnTs*: value=2015-11-04T20:09:01-06:00 
		Line Number '' Description: ' The date and time when the return was created' Type: String(length=63)

		...
	
		
That's a more useful representation of the filing--it also appears roughly in the same order as a paper 990 filing (with the exception of repeating groups, which appear at the end of each schedule). It's also remarkably verbose.

We can narrow in on a single schedule, but first we need to know what is present in this filing, using the --list_schedules option
		 
	
		$ irsx --list_schedules 201533089349301428
	
		['ReturnHeader990x', 'IRS990', 'IRS990ScheduleA', 'IRS990ScheduleB', 'IRS990ScheduleC', 'IRS990ScheduleD', 'IRS990ScheduleG', 'IRS990ScheduleH', 'IRS990ScheduleI', 'IRS990ScheduleJ', 'IRS990ScheduleK', 'IRS990ScheduleL', 'IRS990ScheduleM', 'IRS990ScheduleO', 'IRS990ScheduleR']
	
Now let's look at a human readable text version of schedule J

	$ irsx --format=txt --documentation --schedule=IRS990ScheduleJ 201533089349301428

The output is lengthy: it lists first the schedule parts and then the repeating groups, and for each variable it includes the line number, description and data type of each variable. This is from the section of the output on 'SkdJRltdOrgOffcrTrstKyEmpl':
	
	Repeating Group: SkdJRltdOrgOffcrTrstKyEmpl
	
	
		*ein*: value=941156621 
		Line Number 'NA' Description: 'IRS employer id number' Type: String(9)
	
		*object_id*: value=201533089349301428 
		Line Number 'NA' Description: 'IRS-assigned object id' Type: String(18)
	
		*PrsnNm*: value=Patrick Fry 
		Line Number ' Part II Column (A)' Description: ' Part II contents; Name of officer - person' Type: String(length=35)
	
		*TtlTxt*: value=Trustee, President & CEO SH 
		Line Number ' Part II Column (A)' Description: ' Part II contents; Title of Officer' Type: String(length=100)
	
		*BsCmpnstnFlngOrgAmt*: value=0 
		Line Number ' Part II Column (B)(i)' Description: ' Part II contents; Base compensation ($) from filing organization' Type: BigInteger
	
		*CmpnstnBsdOnRltdOrgsAmt*: value=1523132 
		Line Number ' Part II Column (B)(i)' Description: ' Part II contents; Compensation based on related organizations?' Type: BigInteger
	
		*BnsFlngOrgnztnAmnt*: value=0 
		Line Number ' Part II Column (B)(ii)' Description: ' Part II contents; Bonus and incentive compensation ($) from filing organization' Type: BigInteger
	
		*BnsRltdOrgnztnsAmt*: value=1687050 
		Line Number ' Part II Column (B)(ii)' Description: ' Part II contents; Bonus and incentive compensation ($) from related organizations' Type: BigInteger
	
		*OthrCmpnstnFlngOrgAmt*: value=0 
		Line Number ' Part II Column (B)(iii)' Description: ' Part II contents; Other compensation ($) from filing organization' Type: BigInteger
	
		*OthrCmpnstnRltdOrgsAmt*: value=416185 
		Line Number ' Part II Column (B)(iii)' Description: ' Part II contents; Other compensation ($) from related organizations' Type: BigInteger
	
		*DfrrdCmpnstnFlngOrgAmt*: value=0 
		Line Number ' Part II Column (C)' Description: ' Part II contents; Deferred compensation ($) from filing organization' Type: BigInteger
	
		*DfrrdCmpRltdOrgsAmt*: value=2693377 
		Line Number ' Part II Column (C)' Description: ' Part II contents; Deferred compensation ($) from related organizations' Type: BigInteger
	
		*NntxblBnftsFlngOrgAmt*: value=0 
		Line Number ' Part II Column (D)' Description: ' Part II contents; Nontaxable benefits ($) from filing organization' Type: BigInteger
	
		*NntxblBnftsRltdOrgsAmt*: value=34953 
		Line Number ' Part II Column (D)' Description: ' Part II contents; Nontaxable benefits ($) from related organizations' Type: BigInteger
	
		*TtlCmpnstnFlngOrgAmt*: value=0 
		Line Number ' Part II Column (E)' Description: ' Part II contents; Total of (B)(i) - (D), from filing org' Type: BigInteger
	
		*TtlCmpnstnRltdOrgsAmt*: value=6354697 
		Line Number ' Part II Column (E)' Description: ' Part II contents; Total of (B)(i) - (D), from related orgs' Type: BigInteger
	
		*CmpRprtPrr990FlngOrgAmt*: value=0 
		Line Number ' Part II Column (F)' Description: ' Part II contents; Comp reported prior 990 - from filing org' Type: BigInteger
	
		*CmpRprtPrr990RltdOrgsAmt*: value=396136 
		Line Number ' Part II Column (F)' Description: ' Part II contents; Comp reported prior 990 - from related orgs' Type: BigInteger
 

When looking at compensation, it's important to differentiate between compenstation from the filer -- 'TtlCmpnstnFlngOrgAmt'  which in the above is 0 and 'TtlCmpnstnRltdOrgsAmt' total compensation from related organizations, which is $6,354,697.

The "text" representation is under development and may change, though the underlying json output should not. We can save just that schedule to a file with:

	$ irsx --schedule=IRS990ScheduleJ 201533089349301428 > 201533089349301428.json

### Getting an object id

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



## irsx -- use from python

Much broader functionality is available by running from within python.


	>>> from irsx.runner import XMLRunner
	>>> xml_runner = XMLRunner()
	>>> result = xml_runner.run_filing(201533089349301428)

Result is an array of schedules; each schedule's name can be accessed as result[i]['schedule_name']. Note that this filing has *3* different schedule K's in it. Only schedule K is allowed to repeat--all other lettered schedules (i.e. Schedules A-O and R) may only appear once. If we only care about one schedule we can extract it (though note that the result will still be an array of schedules).

	>>> parsed_filing = xml_runner.run_schedule(201533089349301428, 'IRS990ScheduleJ')
	>>> result = parsed_filing.get_result()

Show the repeating groups that are present this schedule:

	>>> print(result[0]['groups'].keys())
	dict_keys(['SkdJRltdOrgOffcrTrstKyEmpl', 'SkdJSpplmntlInfrmtnDtl'])

	
Show the schedule parts that are present:

	>>> print(result[0]['schedule_parts'].keys())
	dict_keys(['skedj_part_i'])
	
Delve into one:	
	
	>>> key_employees = result[0]['groups']['SkdJRltdOrgOffcrTrstKyEmpl']
	>>> print(len(key_employees))
	20
	>>> key_employees[0].keys()
	
	dict_keys(['object_id', 'ein', 'PrsnNm', 'TtlTxt', 'BsCmpnstnFlngOrgAmt', 'CmpnstnBsdOnRltdOrgsAmt', 'BnsFlngOrgnztnAmnt', 'BnsRltdOrgnztnsAmt', 'OthrCmpnstnFlngOrgAmt', 'OthrCmpnstnRltdOrgsAmt', 'DfrrdCmpnstnFlngOrgAmt', 'DfrrdCmpRltdOrgsAmt', 'NntxblBnftsFlngOrgAmt', 'NntxblBnftsRltdOrgsAmt', 'TtlCmpnstnFlngOrgAmt', 'TtlCmpnstnRltdOrgsAmt', 'CmpRprtPrr990FlngOrgAmt', 'CmpRprtPrr990RltdOrgsAmt'])
	
	>>> for employee in key_employees:                                                                
		  print("[%s] [%s] $%s" % (employee['PrsnNm'], employee['TtlTxt'], employee['TtlCmpnstnRltdOrgsAmt']) )

	[John Boyd] [CAO, MNTL HLTH & CONT CARE SSR] $493297
	[Thomas Blinn] [CEO, Reg Amb Care, SRR] $1007654
	[Pat Brady] [CEO, Sutter Roseville Med. Ctr] $989398
	[James Conforti] [Regional President, SHSSR] $1406818
	[Dennie Conrad] [REG VP, PLNNG & BUS DEV SHSSR] $486103
	[Patrick Fry] [Trustee, President & CEO SH] $6354697
	[Terry Glubka] [CEO, Sutter Solano Medical Ctr] $705442
	[Mitch Hanna] [CAO, SAFH] $647751
	[Sarah Krevans] [COO Sutter Health] $2186723
	[Shelly McGriff] [CNE Sutter Med Ctr Sac.] $477144
	[John Mesic MD] [CMO, Sac Sierra Region] $968939
	[Carrie Owen-Plietz] [CEO, Sutter Med Ctr Sacramento] $934648
	[Anne Platt] [CEO, SUTTER AMADOR HOSPITAL] $579266
	[Thomas Ream II] [Reg CIO, Sac Sierra Region] $424847
	[Jeffrey Sprague] [CFO, Sac Sierra Region (Pt Yr)] $1454430
	[Jeffrey Szczesny] [Reg VP HR, Sac Sierra Region] $633383
	[Paige Terra] [CFO (Part Year)] $657288
	[Janet Wagner] [CAO, Sutter Davis Hospital] $745985
	[PENNY WESTFALL] [VP & REG COUNSEL, SSR] $638189
	[BARBARA NELSON] [CNE, SUTTER ROSEVILLE MED. CTR] $450466






## irsx_index 

### Get the index files, --year[ly]

The IRS maintains annual index files, from 2011 forwards, of what filings have been received electronically and approved for release. Use the utility command, '$ irsx_index' to retrieve them all, or use the --year option to pick just one. Here we just grab 2017. Note that the --verbose flag is on, so that it'll say where the file is saved to. 

	$ irsx_index --year 2017 --verbose
	Getting index file for year: 2017
	Beginning streaming download of https://s3.amazonaws.com/irs-form-990/index_2017.csv
	Total file size: 18.18 MB
	Download completed to /Users/jfenton/github-whitelabel/envs/irsreader_env/lib/python2.7/site-packages/irs_reader/CSV/index_2017.csv in 0:00:02.934290

The location is specified in the settings file, but by default it'll go into a subdirectory of wherever the code is installed called /CSV/. You could set that by modifying the .settings file, but we'll save that for later.

 You could look at the file in a spreadsheet program, and you might want to keep it in your own database, but here I'll just use csvkit (`$ pip install csvkit`) to find something. Note that I'm doing this in the same directory as the file is in, to save typing. 
 
	cd /path/to/virtualenv/lib/python2.7/site-packages/irs_reader/CSV/
	


# Developer directions

#### To use without installing via pip

From the directory with the readme in it, instead of the irsx command, use `$ python -m irs_reader.irsx_cli` so that the command line tools are run as modules and python doesn't freak out. 
You can still add command line args, like this:

		python -m irs_reader.irsx_cli --schedule=ReturnHeader990x --format=txt 201533089349301428
		

## Testing

Nosetests - Test coverage is incomplete

Tox -- see tox.ini; testing for: 2.7,3.5,3.6 . You may need to run `pip install tox` in the testing environment. 

