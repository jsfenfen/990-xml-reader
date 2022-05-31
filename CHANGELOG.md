# IRSX Change Log

All notable changes are documented in this file.


## 0.2.13 - 2022-05-31

Allow version 2020v4.2 to run. Xpaths newly added in 2020 (very few) are still unsupported, but everything else appears to work.


## 0.2.13 - 2021-07-21

Add experimental support for schemas for TY 2020. IRSx will process these now; gathering info about missing xpaths.

## 0.2.12 - 2020-10-23

Bugfix.  

## 0.2.11 - 2020-10-23

Bugfix. 


## 0.2.10 - 2020-10-23

Add support for 2018 schemas through 2018v3.2 and 2018v3.3. Add experimental support for 2019v5.0 through 2019v5.3. 


## 0.2.9 - 2019-10-09

Add support for 2018 schemas through 2018v3.1

## 0.2.8 - 2019-09-15

Update metadata submodule

## 0.2.7 - 2018-08-22

Point to updated 990-xml-metadata repo, which includes xpaths for Tax Years 2017 and 2018. 

## 0.2.6 - 2018-08-22

Allow version 2018v3.0 filings to be processed, these are also in production but were omitted in 0.2.4.


## 0.2.5 - 2018-08-20

Allow xml namespacing, as exhibited by 201940149349301304_public. 

## 0.2.4 - 2018-08-20

Allow version 2018v3.1 filings to be processed. A few new metadata lines will need to be added once I've processed the .xsd files.


## 0.2.3 

PR to accept file cache location as env var - https://github.com/jsfenfen/990-xml-reader/pull/20

## 0.2.2 - 2018-05-09

- Incorporate metadata changes; still need better approach

## 0.2.1 - 2018-05-04

- Updates in metadata to cover 2017; updates downstream. 

## 0.2.0 - 2018-05-03

- Depend on metadata as a submodule instead of as a directory. 
- Change in metadata; instead of a semicolon-delimited list of versions, files instead include version\_start and version\_end which includes the __year__ that a variable first appeared. The version_end is left blank unless the variable is no longer used.

## 0.1.1 - 2018-03-19

- Added the object_id to the .csv output
- Added IRSX\_SETTINGS\_LOCATION to allow: `from irs_reader.settings import IRSX_SETTINGS_LOCATION`

## 0.0.10 - 2018-03-15

- Initial release



## details

The format is based on [Keep a Changelog](http://keepachangelog.com/); with a goal of [semantic versioning](http://semver.org/).
