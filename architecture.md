## Architectural Overview

This is an overview of how different pieces of the irsx project work together. There are lots of different repos, on the theory that each do just one thing. Most users will need only worry about reading the files, and understanding all the connected pieces is not required for that.

## Introduction

The 990 data comes with three forms (990, 990EZ, 990PF), 16 possible [lettered schedules](https://www.documentcloud.org/documents/4433426-ReturnData990-XSD.html#document/p1/a416081) and more than 300 minor possible [other forms](https://www.documentcloud.org/documents/4433426-ReturnData990-XSD.html#document/p1/a416082). The xml corpus now contains filings with schema years dating as far back as 2009. There have been more than 30 production versions since then, and while most new versions have few changes, the schemas were mostly rewritten between 2012 and 2013.

IRSx can read xml schemas from 2013 forwards. The groups.csv file has been standardized as far back as 2010, to allow for csv output of earlier era filings. There's a larger collaborative effort to standardize all of the possible xpaths underway via the nonprofit open data consortium. We plan to add their more "human readable" names once they are compatible (there are some issues that still need to be worked out). 

The overall project is broken up into a number of parts.

[990-xml-admin](https://github.com/jsfenfen/990-xml-admin) reads the schema files and has been used to standardize variables and variable types across versions. The result of it's standardization process are the metadata files: metadata .csv files: schedule\_parts, groups, variables, line\_numbers, descriptions.

[IRSx](https://github.com/jsfenfen/990-xml-admin), or 990-xml-reader, reads files into useful outputs. It uses the metadata .csv files to make sense of the filings.

There's a separate database repo [990-xml-database](https://github.com/jsfenfen/990-xml-database) that depends on IRSx, that uses the metadata to generate a database schema or django models file and loads filings en masse so they can be queried with a relational database. This requires django and postgresql. The database repo can also bake out the documentation site at [irsx.info](http://www.irsx.info).

## Ongoing operation

It's unclear if we will have schema files on a timely basis, it's important to consider what an update will look like if we don't have a schema file. 

Under that scenario, it should be possible to human-edit the variables.csv file to change or tweak variables. 

When IRSx hits a legal version that contains an xpath that's not known, it records a "key error". The database repo includes entry code that logs key errors as part of loading. The general idea is that a monthly update might also include a step that looks for new xpaths and adds them, potentially manually. This might mean that new metadata files are the downstream of the database repo.

A cleaner solution is to pregenerate all possible xpaths by using the schema files. Then it's just a matter of matching existing xpaths, as well as determining whether new ones are newly created or a modification of an existing xpath. The IRS schemas in the past contained file 'diffs' which helped identify where changes had taken place. 