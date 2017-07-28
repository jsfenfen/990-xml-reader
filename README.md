# xirsx
### Turn the IRS' versioned XML 990's into python objects aware of the version-specific line number, description and data type 

This is a python library and command line tool to simplify working with nonprofit tax returns released by the IRS in XML format. 

It is under development and some capabilities have yet to be implemented.

The IRS identifies electronic filings by their object_id, available in the annual index files released [link].

## Installation

#### The directions below are a hack--we should put this on PyPI when released
 
- git clone the repo 
- install locally using `$ pip install . ` from the directory with setup.py in it. It's painfully slow. You should now be able to run it as a command line utility, i.e. $ xirsx --help or $ xirsx_index --help
- To uninstall use `$ pip uninstall xirsx`
- To see if it's installed, run `$ pip freeze`; if you see a line line 'xirsx==0.0.1' it is installed. 


## xirsx -- command line
Use the object_id to reference a particular filing.


		$ xirsx --list_schedules 201642229349300909
		['ReturnHeader990x', u'IRS990', u'IRS990ScheduleA',
		 u'IRS990ScheduleB', u'IRS990ScheduleD', u'IRS990ScheduleM',
		 u'IRS990ScheduleO']
		 
Save it to a file by redirecting the output: 
		
		$ xirsx --schedule IRS990 --format json 201642229349300909 > 2016_990.json

This is a json representation of the form as it appears--we have no standardized variables across versions at all in this representation.
	
	


		usage: xirsx [-h] [--verbose]
		             [--schedule {IRS990,IRS990EZ,IRS990PF,IRS990ScheduleA,IRS990ScheduleB,IRS990ScheduleC,IRS990ScheduleD,IRS990ScheduleE,IRS990ScheduleF,IRS990ScheduleG,IRS990ScheduleH,IRS990ScheduleI,IRS990ScheduleJ,IRS990ScheduleK,IRS990ScheduleL,IRS990ScheduleM,IRS990ScheduleN,IRS990ScheduleO,IRS990ScheduleR,ReturnHeader990x}]
		             [--format {dict,json}] [--list_schedules] [--encoding ENCODING]
		             N [N ...]
			
		positional arguments:
		  N                     object ids
			
		optional arguments:
		  -h, --help            show this help message and exit
		  --verbose             Verbose output
		  --schedule {IRS990,IRS990EZ,IRS990PF,IRS990ScheduleA,IRS990ScheduleB,IRS990ScheduleC,IRS990ScheduleD,IRS990ScheduleE,IRS990ScheduleF,IRS990ScheduleG,IRS990ScheduleH,IRS990ScheduleI,IRS990ScheduleJ,IRS990ScheduleK,IRS990ScheduleL,IRS990ScheduleM,IRS990ScheduleN,IRS990ScheduleO,IRS990ScheduleR,ReturnHeader990x}
		                        Get only that schedule
		  --format {dict,json}  Output format
		  --list_schedules      Only list schedules
		  --encoding ENCODING   encoding (probably utf-8)


## xirsx -- use from python


	>>> from xirsx.filing import Filing
	>>> f = Filing(201642229349300909)
	>>> f.process()
	>>> f.get_version() # 2015v2.1
	>>> schedules = f.get_schedules()
	[u'IRS990', u'IRS990ScheduleA', u'IRS990ScheduleB', u'IRS990ScheduleD', u'IRS990ScheduleM', u'IRS990ScheduleO']
	>>> for sked in schedules:
	>>>  print("\n\n%s \n%s" % (sked, f.get_schedule(sked) ) ) 



## Introduction to the IRS' MEF 990 XML

### xirsx_index : Get the index files, --year[ly]

The IRS maintains annual index files, from 2011 forwards, of what filings have been received electronically and approved for release. Use the utility command, '$ xirsx_index' to retrieve them all, or use the --year option to pick just one. Here we just grab 2017. Note that the --verbose flag is on, so that it'll say where the file is saved to. 

	$ xirsx_index --year 2017 --verbose
	Getting index file for year: 2017
	Beginning streaming download of https://s3.amazonaws.com/irs-form-990/index_2017.csv
	Total file size: 18.18 MB
	Download completed to /Users/jfenton/github-whitelabel/envs/irsreader_env/lib/python2.7/site-packages/irs_reader/CSV/index_2017.csv in 0:00:02.934290

The location is specified in the settings file, but by default it'll go into a subdirectory of wherever the code is installed called /CSV/. You could set that by modifying the .settings file, but we'll save that for later.

 You could look at the file in a spreadsheet program, and you might want to keep it in your own database, but here I'll just use csvkit (`$ pip install csvkit`) to find something. Note that I'm doing this in the same directory as the file is in, to save typing. 
 
	cd /path/to/virtualenv/lib/python2.7/site-packages/irs_reader/CSV/
	


# Dev directions

#### To use without installing via pip

- from the directory with the readme in it, instead of the xirsx command, use `$python -m python -m irs_reader.cli` or `$python -m irs_reader.cli_index` (for xirsx_index) so that the command line tools are run as modules and python doesn't freak out. 


## Testing

Nosetests - Test coverage is incomplete

Tox -- see tox.ini; testing for: 2.7,3.5,3.6 . You may need to run `pip install tox` in the testing environment. 

