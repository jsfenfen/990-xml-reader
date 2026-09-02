# IRSx

IRSx is a python library and command line tool for parsing IRS Form 990 XML tax returns into structured, standardized data--either json or csv. It supports forms 990, 990-EZ, 990-PF, and all lettered schedules (A-O and R) for schema versions from 2013 to the present. CSV and TXT output is also available for schemas back to 2010.

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Downloading filings](#downloading-filings)
- [Quickstart](#quickstart)
- [Bulk processing](#bulk-processing)
- [Command line usage](#command-line-usage)
- [Output formats: json, csv, txt](#output-formats-json-csv-txt)
- [CSV/TXT examples](#csv--txt-examples)
- [JSON examples](#json-examples)
- [Find a tax return's object_id](#getting-an-object-id)
- [Variable errors and deprecated return values](#variable-errors-and-deprecated-values)
- [Configuring the file cache directory](#configuring-the-file-cache-directory)
- [IRSx as a python library](#irsx-from-python)
- [IRSx Reference](#irsx-reference)
- [irsx_index: yearly index files](#irsx_index)
- [Developer directions](#developer-directions)
- [Testing](#testing)
- [Acknowledgements](#acknowledgements)

## Installation

    $ pip install irsx

To upgrade:

    $ pip install irsx --upgrade

## Requirements

Python 3.11 or later. Dependencies: `requests`, `xmltodict`.

## Downloading filings

The IRS publishes bulk XML filing downloads at [this page](https://www.irs.gov/charities-non-profits/form-990-series-downloads). Use `irsx_retrieve` to download and extract all filings for a given year:

    $ irsx_retrieve 2024
    $ irsx_retrieve 2023 2024 --verbose

This scrapes the IRS downloads page to discover available zip files, downloads them, extracts the XML files, and removes the zip files. Supports years 2019 through the present.

Files are extracted to the working directory (configurable via `IRSX_WORKING_DIRECTORY` environment variable, defaults to `irs_reader/XML/`).

You can also retrieve filings--or perhaps data shaped to your purpose--at the [Giving Tuesday project](https://990data.givingtuesday.org/#datasets). 

## Quickstart

IRSx can be used as a command line tool or as a python library.

We'll use the object_id `201533089349301428`, which corresponds to the file `201533089349301428_public.xml` (it's part of this git repo, so you don't need to download it). The first four digits of the object id represent the tax year it covers; it was released by the IRS during 2026, so it appears in that file.  

To dump the filing as a human-readable CSV:

    $ irsx --format=csv 201533089349301428 --input-dir ./xml/2015

To view just one schedule in text format:

    $ irsx --format=txt --schedule=IRS990ScheduleJ --input-dir ./xml/2015 201533089349301428

As a python library:

    >>> from irsx.xmlrunner import XMLRunner
    >>> xml_runner = XMLRunner()
    >>> parsed_filing = xml_runner.run_sked(201533089349301428, 'IRS990ScheduleJ',
    ...     filepath='./xml/2015/201533089349301428_public.xml')
    >>> key_employees = parsed_filing.get_result()[0]['groups']['SkdJRltdOrgOffcrTrstKyEmpl']
    >>> for employee in key_employees:
    ...  print("Name:%s, Base Compensation, related orgs $%s" % (employee['PrsnNm'], employee['CmpnstnBsdOnRltdOrgsAmt']))



## Bulk processing

Use `irsx_bulk` to parse many filings in parallel:

    $ irsx_bulk /path/to/xml --output-dir /path/to/output
    $ irsx_bulk /path/to/xml --output-dir /path/to/output --format csv
    $ irsx_bulk /path/to/xml --output-dir /path/to/output --format jsonl
    $ irsx_bulk /path/to/xml --output-dir /path/to/output --workers 8

To process all filings for a specific year:

    $ irsx_bulk --year 2024 --output-dir parsed/2024
    $ irsx_bulk --year 2024 --input-dir /data/xml --output-dir parsed/2024

Options:

- `--format json` (default): one JSON file per filing
- `--format csv`: one CSV file per filing
- `--format jsonl`: all filings in a single `filings.jsonl` file (one JSON object per line, less file I/O overhead)
- `--workers N`: number of parallel worker processes (default: number of CPUs)
- `--skip-existing`: skip filings that already have output files (json/csv only)
- `--verbose`: print per-file errors
- `--pattern '*.xml'`: glob pattern for input files

Progress stats are printed every 100 files:

    [300/45000] 412 files/sec | 2 errors | 8 workers | 7s elapsed

The standardizer (metadata) is loaded once per worker process and reused across all filings that worker handles.

## Command line usage

Installing the library installs three command line tools plus the bulk processor:

- `irsx` -- parse individual filings
- `irsx_index` -- download yearly index files
- `irsx_retrieve` -- download bulk XML files from the IRS
- `irsx_bulk` -- parallel bulk parsing

### irsx

    $ irsx 201533089349301428                                    # JSON output
    $ irsx --format=csv 201533089349301428                       # CSV output
    $ irsx --format=txt --schedule=IRS990ScheduleJ 201533089349301428  # TXT, one schedule
    $ irsx --list_schedules 201533089349301428                   # list available schedules
    $ irsx --file output.json 201533089349301428                 # write to file

Full usage:

    usage: irsx [-h] [--verbose]
                [--schedule {IRS990,IRS990EZ,...,ReturnHeader990x}]
                [--xpath] [--format {json,csv,txt}] [--file FILE]
                [--list_schedules]
                object_ids [object_ids ...]

## Output formats: json, csv, txt

- **JSON**: Nested structure with consistent variable names across all schema versions (2013+). Best for programmatic use and database loading.
- **CSV**: Transposed format — each row is a variable with its xpath, line number, description, and value. Available for 2010+. Best for spreadsheet viewing.
- **TXT**: Human-readable text dump, similar to CSV but formatted for terminal/text editor viewing. Available for 2010+.

JSON output uses "canonical" variable names standardized to 2016v3.0. CSV and TXT use version-specific line numbers and descriptions.

### CSV / TXT examples

List available schedules:

    $ irsx --list_schedules 201533089349301428 --input-dir ./xml/2015

    ['ReturnHeader990x', 'IRS990', 'IRS990ScheduleA', 'IRS990ScheduleB', ...]

View schedule J as text:

    $ irsx --format=txt --schedule=IRS990ScheduleJ --input-dir ./xml/2015 201533089349301428

Excerpt:

    ****************
      Value: '296489'
    Form: IRS990ScheduleJ
    Line:Part II Column (B)(ii)
    Description:Part II contents; Bonus and incentive compensation ($) from related organizations
    Group: SkdJRltdOrgOffcrTrstKyEmpl group_index 1

The "Group" variable corresponds to `db_name` in `groups.csv`. The `group_index` increments with each occurrence of a repeating group.

### JSON examples

    $ irsx 201533089349301428 --input-dir ./xml/2015

The return structure is an array of schedules:

    [
      {
        "schedule_name": "<Schedule Name>",
        "schedule_parts": {
          "<part_name>": { ... variables ... }
        },
        "groups": {
          "<group_name>": [
            { ... variables ... },
            ...
          ]
        }
      },
      ...
    ]

Each schedule part or repeating group includes the `object_id` and `ein`. Only schedules, parts, and groups with values are included.

## Getting an object id

The IRS maintains annual index files of electronically-filed returns. Use `irsx_index` to download them:

    $ irsx_index --year 2017

The index files contain columns: `RETURN_ID`, `FILING_TYPE`, `EIN`, `TAX_PERIOD`, `SUB_DATE`, `TAXPAYER_NAME`, `RETURN_TYPE`, `DLN`, `OBJECT_ID`.

Example using csvkit to search:

    $ csvcut -c 3,4,6,9 index_2016.csv | grep 'SUTTER HEALTH'
    941156621,201412,SUTTER HEALTH SACRAMENTO SIERRA REGION,201533089349301428

## Variable errors and deprecated values

When IRSx encounters an xpath not defined in the metadata, it logs it as a keyerror. You can retrieve keyerrors from any filing:

    completed_filing = xml_runner.run_filing(FILING_ID)
    keyerrors = completed_filing.get_keyerrors()



## Configuring the file cache directory

### Environment variables

    $ export IRSX_CACHE_DIRECTORY=/path/to/irsx
    $ irsx --format=csv 201533089349301428 --input-dir ./xml/2015
    # XML at ./xml/2015/201533089349301428_public.xml

    $ irsx_index --year 2017
    # CSV at /path/to/irsx/CSV/index_2017.csv

For finer control:

- `IRSX_WORKING_DIRECTORY` — where XML files are stored
- `IRSX_INDEX_DIRECTORY` — where index CSV files are stored

### Legacy configuration

You can also set paths via `local_settings.py`:

    >>> from irsx.settings import IRSX_SETTINGS_LOCATION
    >>> IRSX_SETTINGS_LOCATION
    '/path/to/site-packages/irsx/settings.py'

Copy `local_settings.py-example` to `local_settings.py` in that directory and edit `WORKING_DIRECTORY`.

## IRSx from python

    >>> from irsx.xmlrunner import XMLRunner
    >>> xml_runner = XMLRunner()
    >>> parsed_filing = xml_runner.run_filing(201533089349301428, filepath='/path/to/xml/201533089349301428_public.xml')
    >>> result = parsed_filing.get_result()  # Array of parsed schedules
    >>> schedule_list = parsed_filing.list_schedules()

    >>> import json
    >>> for sked in result:
    ...  print("Schedule: %s" % sked['schedule_name'])
    ...  print(json.dumps(sked, indent=4, sort_keys=True))

Schedule K can repeat (bond schedules allow 4 entries per form):

    >>> skedk = parsed_filing.get_parsed_sked('IRS990ScheduleK')
    >>> len(skedk)
    3

Extract just one schedule:

    >>> parsed_filing = xml_runner.run_sked(201533089349301428, 'IRS990ScheduleJ')
    >>> result = parsed_filing.get_result()

    >>> key_employees = result[0]['groups']['SkdJRltdOrgOffcrTrstKyEmpl']
    >>> for employee in key_employees:
    ...  print("[%s] [%s] $%s" % (employee['PrsnNm'], employee['TtlTxt'], employee['TtlCmpnstnRltdOrgsAmt']))

    [John Boyd] [CAO, MNTL HLTH & CONT CARE SSR] $493297
    [Thomas Blinn] [CEO, Reg Amb Care, SRR] $1007654
    ...

## IRSx Reference

Variables are described in the [metadata CSV files](https://github.com/jsfenfen/990-xml-metadata):

- `variables.csv` — xpath-to-variable mappings
- `groups.csv` — repeating group definitions
- `schedule_parts.csv` — form part organization
- `line_numbers.csv` — version-specific line numbers
- `descriptions.csv` — version-specific descriptions

More detail at [irsx.info](http://irsx.info/).

## irsx_index

Download the IRS yearly index files (2011-present):

    $ irsx_index --year 2017 --verbose
    $ irsx_index                        # download all years

## Developer directions

### Running without installing via pip

From the repo root, use `python -m` to run modules directly:

    $ python -m irs_reader.irsx_cli --format=txt 201533089349301428
    $ python -m irs_reader.irsx_retrieve_cli 2024
    $ python -m irs_reader.irsx_bulk_cli /path/to/xml --output-dir /path/to/output
    $ python -m irs_reader.irsx_bulk_cli --year 2024 --output-dir parsed/2024

## Testing

Tests use pytest. Run the full suite:

    $ pip install pytest
    $ python -m pytest test_irsx.py -v

Run a subset:

    $ python -m pytest test_irsx.py -k "Bulk" -v
    $ python -m pytest test_irsx.py -k "Standardizer" -v

## Acknowledgements

This project was originally built for ProPublica, an independent, nonprofit newsroom that runs [NonProfit Explorer](http://projects.propublica.org/nonprofits/).

Thanks to Tyler Davis for testing and suggesting improvements.
