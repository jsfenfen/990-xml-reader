# IRSX Change Log

All notable changes are documented in this file.


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
