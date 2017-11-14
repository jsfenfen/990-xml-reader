# IRSx

## Table of Contents

- [Quickstart](#quickstart)
- [About](#about)
- [Installation](#installation)
- [Command line IRSx](#command-line-irsx)
- [Output formats: json, csv, txt](#command-line-output-formats-json-csv-txt)
- [CSV/TXT examples](#csv--txt-examples)
- [JSON examples](#json-examples)
- [Find a tax return's object_id](#getting-an-object-id)
- [Variable errors and deprecated return values](#variable-errors-and-deprecated-values)
- [IRSx as a python library](#irsx-from-python)
- [irsx_index: get yearly index files](#irsx_index) 
- [Developer directions](#developer-directions)
- [Testing](#testing)

## Quickstart
We're using the "object_id" 201533089349301428 to refer to the Dec. 2014 990 filed by "Sutter Health Sacramento Region", which is described in the [2016 index file](https://s3.amazonaws.com/irs-form-990/index_2016.csv).  To make the file human readable, use the txt format option, and only display one schedule (the complete command line usage is available with --help). 

	$ irsx --format=txt --schedule=IRS990ScheduleJ 201533089349301428

The result should look something like:  

		Schedule IRS990ScheduleJ
	
	Line:Part I Line 1a Description:Idemnification and gross-up payments Xpath:/IRS990ScheduleJ/IdemnificationGrossUpPmtsInd
	Value=X 
	Group:
	
	Line:Part I Line 1b Description:Written policy reference T and E expenses? Xpath:/IRS990ScheduleJ/WrittenPolicyRefTAndEExpnssInd
	Value=true 
	Group:
	... [ truncated, the full output is quite lengthy ]
	

We can use it as a python library to pull out specific pieces of data, across versions

	>>> from irsx.xmlrunner import XMLRunner
	>>> xml_runner = XMLRunner()
	>>> parsed_filing = xml_runner.run_sked(201533089349301428, 'IRS990ScheduleJ')
	>>> key_employees = parsed_filing.get_result()[0]['groups']['SkdJRltdOrgOffcrTrstKyEmpl']
	>>> for employee in key_employees:                                                                
		  print(employee['PrsnNm'])



## About

IRSx is a python library and command line tool to simplify working with nonprofit tax returns [released](https://aws.amazon.com/public-datasets/irs-990/) by the IRS in XML format. The library currently standarizes returns submitted in formats dating from 2013 and forwards into consistently named datastructures that follow the same format as the "paper" 990. Repeating elements, such as the salary disclosed for best compensated employees, appear at the end of each schedule. We plan to release updated metadata that will allow processing of earlier forms.

Forms from schemas years ranging from 2010 to the present are 'viewable' in CSV and TXT mode via the command line tool.

From the command line, xml files can be output as machine readable json, csv or human readable text. From within a python program, the results are returned as native data structures. 

Filers are allowed to leave blank tax lines not applicable to them. IRSx returns only schedules and lines that have been completed by filers.

The tax returns are complex--the easiest way to understand them is to consult the [metadata csv files](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/metadata), and cross reference these to the forms in [sample\_schedules](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/sample_schedules) (which contains recent pdf versions of the schedules).  The data returned for each schedule read contains schedule parts (see the [schedule\_parts.csv](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/metadata/schedule_parts.csv) for all possible parts) and repeating groups (see [groups.csv](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/metadata/groups.csv)) that occur within that schedule. Both repeating groups and schedule\_parts contain variables, which are documented in the [variables.csv](https://github.com/jsfenfen/990-xml-reader/tree/master/irs_reader/metadata/variables.csv) table. 





## Installation

#### Will be easier once we put this on pypi
 
- git clone the repo 
- install locally using `$ pip install . ` from the directory with setup.py in it. It's painfully slow. You should now be able to run it as a command line utility, i.e. $ irsx --help or $ irsx_index --help
- To uninstall use `$ pip uninstall irsx`
- To see if it's installed, run `$ pip freeze`; if you see a line line 'irsx==0.0.1' it is installed. 


## Command line IRSx
Installing the library will also install the irsx command line tool, which uses the IRS' object\_ids to reference a particular filing. By default results are printed to the terminal, but can be saved to a specific file with the `--file` option. Using the `--verbose` flag will display a bit more information about what's happening, but should not be used if you're trying to capture the output into a file (as it won't follow the format needed). 

## CLI Output formats: json, csv, txt

The command line tool supports three styles of 'displaying' a filing. The output can also be written out to a file specified with the `--file` option. 

For browsing and human-reference, csv or text is often easier to understand, because it maintains the order of the original filing. For bulk use or database entry, json is probably more relevant, because the "structure" of the original database--broken into parts, some repeating--is better replicated in those. 

The csv output is "transposed" from a normal csv--in other words, each *row* represents a variable. Repeating variables may appear multiple times (though the 'group_index' should increment with each new occurence).

JSON output is only available for schema versions from 2013 and later. CSV and TXT output are available for 2010 schemas and later. 

- __JSON__ The first is a nested-json structure that provides a consistent way of describing variables for all schema versions from 2013 and forwards. The down side of this is that json is not ordered, so it can be confusing for humans to view. The description and line number fields are for the "canonical" version--2016v3.0--and so may vary from those seen on the form. 
- __CSV__ This isn't a 'real' csv file, it's really a listing of all the different variables found, along with metadata like line number and description. It's available for versions 2010 and forwards. This doesn't attempt to restructure the content, it just spits it out in the order that it appears. This is often more human readable than json. Because it's a listing of all variables, the xpaths to those variables may repeat. A group_index column keeps count of which repeating group each variable belongs to. Both CSV and TXT formats use line numbers and descriptions that are specific to the version (these can both change over time) so it's 
- __TXT__ There's also a txt format output that is very similar to csv in that it prints the rows it finds in an ordered dump, but makes it slightly more readable. CSV is intended to be viewed in a spreadsheet program, whereas TXT format translates better to a text editor / wider than normal terminal window.

### CSV / TXT examples


CSV and TXT are often more useful for browsing a file--we can eyeball the whole filing, but sometimes it's handy to zero in on just one schedule. Irsx has a shortcut, the --list_schedules option to show you what's available.
		 
	
		$ irsx --list_schedules 201533089349301428
	
		['ReturnHeader990x', 'IRS990', 'IRS990ScheduleA', 'IRS990ScheduleB', 'IRS990ScheduleC', 'IRS990ScheduleD', 'IRS990ScheduleG', 'IRS990ScheduleH', 'IRS990ScheduleI', 'IRS990ScheduleJ', 'IRS990ScheduleK', 'IRS990ScheduleL', 'IRS990ScheduleM', 'IRS990ScheduleO', 'IRS990ScheduleR']
	
Now let's look at a human readable text version of schedule J

	$ irsx --format=txt --schedule=IRS990ScheduleJ 201533089349301428

Note that the --schedule argument also works in json or csv mode.

The output is lengthy, but let's look at an excerpt:

	Line:Part II Column (A) Description:Part II contents; Name of officer - person Xpath:/IRS990ScheduleJ/RltdOrgOfficerTrstKeyEmplGrp/PersonNm
	Value=Patrick Fry 
	Group: SkdJRltdOrgOffcrTrstKyEmpl group_index 5
	
	Line:Part II Column (A) Description:Part II contents; Title of Officer Xpath:/IRS990ScheduleJ/RltdOrgOfficerTrstKeyEmplGrp/TitleTxt
	Value=Trustee, President & CEO SH 
	Group: SkdJRltdOrgOffcrTrstKyEmpl group_index 5
	
	Line:Part II Column (B)(i) Description:Part II contents; Base compensation ($) from filing organization Xpath:/IRS990ScheduleJ/RltdOrgOfficerTrstKeyEmplGrp/BaseCompensationFilingOrgAmt
	Value=0 
	Group: SkdJRltdOrgOffcrTrstKyEmpl group_index 5
	
	Line:Part II Column (B)(i) Description:Part II contents; Compensation based on related organizations? Xpath:/IRS990ScheduleJ/RltdOrgOfficerTrstKeyEmplGrp/CompensationBasedOnRltdOrgsAmt
	Value=1523132 
	Group: SkdJRltdOrgOffcrTrstKyEmpl group_index 5
 
 Note the "Group" variable. This corresponds to the db_name in the groups.csv file in the metadata directory. It is only listed if a variable is part of a "repeating group" (like officers / trustees / key employees). The "group\_index" variable represents the number of times this variable has been seen.
 


### JSON examples



	$ irsx 201533089349301428
	[{"schedule_name": "ReturnHeader990x", "groups": {}, "schedule_parts": {"returnheader990x_part_i": {"object_id": 201533089349301428, "ein": "941156621", "RtrnHdr_RtrnTs": "2015-11-04T20:09:01-06:00",...

This will just spit out a json representation of the entire filing. See more about how to get an IRS object_id and how to read the data format that's returned below.


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



### Complete command line usage
This is available with the --help option

	usage: irsx [-h] [--verbose]
	            [--schedule {IRS990,IRS990EZ,IRS990PF,IRS990ScheduleA,IRS990ScheduleB,IRS990ScheduleC,IRS990ScheduleD,IRS990ScheduleE,IRS990ScheduleF,IRS990ScheduleG,IRS990ScheduleH,IRS990ScheduleI,IRS990ScheduleJ,IRS990ScheduleK,IRS990ScheduleL,IRS990ScheduleM,IRS990ScheduleN,IRS990ScheduleO,IRS990ScheduleR,ReturnHeader990x}]
	            [--no_doc] [--format {json,csv,txt}] [--file FILE]
	            [--list_schedules]
	            object_ids [object_ids ...]
	
	positional arguments:
	  object_ids            object ids
	
	optional arguments:
	  -h, --help            show this help message and exit
	  --verbose             Verbose output
	  --schedule {IRS990,IRS990EZ,IRS990PF,IRS990ScheduleA,IRS990ScheduleB,IRS990ScheduleC,IRS990ScheduleD,IRS990ScheduleE,IRS990ScheduleF,IRS990ScheduleG,IRS990ScheduleH,IRS990ScheduleI,IRS990ScheduleJ,IRS990ScheduleK,IRS990ScheduleL,IRS990ScheduleM,IRS990ScheduleN,IRS990ScheduleO,IRS990ScheduleR,ReturnHeader990x}
	                        Get only that schedule
	  --no_doc              Hide line number, description, other documentation
	  --format {json,csv,txt}
	                        Output format
	  --file FILE           Write result to file
	  --list_schedules      Only list schedules




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



## irsx from python 

Much broader functionality is available by running from within python.


	>>> from irsx.xmlrunner import XMLRunner
	>>> xml_runner = XMLRunner()
	>>> result = xml_runner.run_filing(201533089349301428)

Result is an array of schedules; each schedule's name can be accessed as result[i]['schedule_name']. Note that this filing has *3* different schedule K's in it. Only schedule K is allowed to repeat--all other lettered schedules (i.e. Schedules A-O and R) may only appear once. If we only care about one schedule we can extract it (though note that the result will still be an array of schedules).

	>>> parsed_filing = xml_runner.run_sked(201533089349301428, 'IRS990ScheduleJ')
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



### Variable errors and deprecated values

In normal operation variable errors--where tax returns specify a value that's not defined in the schema files--should not be a frequent occurrence, and can be suggestive of larger problems. This section is intended mainly for testing, development, or adding new schema versions. 

To understand which variables are not recorded, or missed, you need to know a bit about how xml is represented. Consider this snipped:

		<PreparerFirmGrp>
	      <PreparerFirmEIN>820343828</PreparerFirmEIN>
	      <PreparerFirmName>
	        <BusinessNameLine1Txt>COOPER NORMAN</BusinessNameLine1Txt>
	      </PreparerFirmName>
	      <PreparerUSAddress>
	        <AddressLine1Txt>PO BOX 5399</AddressLine1Txt>
	        <CityNm>TWIN FALLS</CityNm>
	        <StateAbbreviationCd>ID</StateAbbreviationCd>
	        <ZIPCd>833035399</ZIPCd>
	      </PreparerUSAddress>
	    </PreparerFirmGrp>
	    
The individual variables can be referred to by the "xpath" to them (a slash-separated record of the element hierarchy), so for instance, the name of the business that completed this return is /PreparerFirmGrp/PreparerFirmName/BusinessNameLine1Txt . That assumes this element is the "root", but the full path to this element (which is in the returnheader section) is this: /Return/Returnheader/PreparerFirmGrp/PreparerFirmName/BusinessNameLine1Txt.

Imagine the return includes a BusinessNameLine3Txt -- in other words, a value with the xpath /PreparerFirmGrp/PreparerFirmName/BusinessNameLine3Txt . That's unlikely to happen--the IRS has validation software that would likely prevent this from being submitted. If irsx encounters a variable that's not defined in variables CSV it simply ignores it and logs it as a keyerror. You can retrieve the keyerrors from any filing using the library.   

	 
	completed_filing  = self.xml_runner.run_filing(FILING_ID)
	if completed_filing.get_keyerrors(): # Returns True / False
        keyerrors = completed_filing.get_keyerrors()
        

The return value should be a list of dictionaries like this:  

	[ 'schedule_name': NAME, 
	  'keyerrors':
	  		['element_path': XPATH_ERROR, 
	  		 'element_path': XPATH_ERROR, 
	  		 ...
	
	  		]
	 ]

By far the biggest source of keyerrors are tax return items that no longer occur on current forms. 

Irsx works by turning a version-specific representation of a tax return (the original xml filing) into a standardized representation modeled on 2016v3.0. In other words, it tries to transform prior year tax forms into a canonical version.  For variables that have been removed, there's no canonical version. In the future, these variables will be tracked in a separate location.  



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

Nosetests - Test coverage is incomplete, improve it with coverage.py ( so run 'pip install coverage' 
then:

	$ nosetests --with-coverage --cover-erase --cover-package=irs_reader

or

	$ coverage report -m 



Tox -- see tox.ini; testing for: 2.7,3.4,3.5,3.6. You may need to run `pip install tox` in the testing environment. 

