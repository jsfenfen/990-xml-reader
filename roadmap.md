# IRSx Roadmap

This is a general guide to next steps on the IRSx project. Many of these improvements may entail changes to code in other (related) repositories, but I'm putting the whole thing here. 

For more on how various related repositories relate, see the [architectural overview](https://github.com/jsfenfen/990-xml-reader/blob/master/architecture.md). This is probably a lot more information than most casual users will want--this guide is intended to help folks interesting in understanding the process and what lies ahead.

This is kinda just a collection of active tickets put in one place.

## Separate metadata from data

The .csv files in the metadata directory: variables, groups, schedule\_parts, line\_numbers and descriptions represent a way of documenting the .xsd files, and are useful for turning the raw xml into something that can go into a database.

While the IRSx project is written in python, the metadata .csv files should allow other folks to write code against them in other languages. 

## Add ground-truth testing

The tests written to date assess whether the code runs error-free, but a more detailed approach is required to show that the output is correct. During the Aspen Institute's validatathon volunteers checked that some .csv files were in fact correct. They need to be posted (probably to a separate repo) and then code needs to be written to test that the output is correct. There may be minor bits of munging (not sure about spaces; the csv files were edited by humans in google spreadsheets); also note that the json output doesn't preserver original order (that's due to the json spec--it's not supposed to be ordered) so that will need to be addressed in the code as well.




## Bootstrap across the 2012-2013 gap with Nonprofit Open Data Coalition files

The nonprofit open data coalition project to standardize names across all versions is mostly complete, though some bugs remain. We're looking to do this in the second half of 2018.

Using the concordance file, it should be possible to add xpath data for most xpaths going back to 2010. Using routines from irs-990-admin, should double check that data types are compatible.

Note that groups.csv has already been updated with the group 'root' elements going back to 2010. That's key. Schema year 2009 has many changes too, at the moment I'm just looking to add prior years back to 2010.


 

## Renovate or rewrite irs-990-admin 

irs-990-admin is the oldest part of the project, runs python 2.7ish, and is responsible for reading .xsd schema files and generating the complete database structure. There are a fair number of one-off regexes to fix bulk xpath changes between versions. 

But fundamentally, the mission has changed. 990-admin was written to come up with a standardized set of names and associated database fields by looking at all applicable versions, but the problem going forward is how to add new schemas. Instead of "rebasing" the schemas on new canonical versions, instead we want to only add new xpaths that don't exist already. Probably a much lighter weight repo is needed, but note that parsing .xsd is complex. 

This repo is probably needed to bootstrap across the 2012-2013 routine. One of the biggest concerns is consistent data types, as IRS can change field size in any version (though rarely does).

The models in this repo are for the captured section of xsd, so it's useful for tracking version-specific questions (e.g. when did the "application pending checkbox" get commented out)

## Incorporate 1023EZ filings

Since mid 2014 1023 filings have been public. Add them to 990-irs-database. 

## Explore a way of distributing the annual index files in a way that IRSx can search them

It's easy enough for advanced users to dump the complete record of index files in a database, and there are scripts for doing so in 990-xml-database. But casual users who want information that's in the index files (but not the body of the filing) don't have a simple way of doing it. Grepping the files or using csvkit are one approach. It would be great if there was a simple way to load this into a file-based sqlite db that could be queried, not quite sure of the logistics of doing this. Is there something memory-reasonable that's better than a table scan for every search--but maybe that's premature optimization.  A table scan, after all, works.

## Adoption of ongoing schema changes

IRS990_admin was written before it was clear what the output needed to be. With a clearer set of goals, it should probably be possible to write a much terser parser expressly for the purpose of checking for new filings and adding new entries to the appropriate metadata files? 

That said, the initial approach, which tracks individual elements in versions, is really useful when doing more complex operations, like verifying data types, across years.

It should be possible to capture "key errors" as they occur in new versions in a running version of 990-xml-database, and add new variables manually as needed. 
