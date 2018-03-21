# Yes, the 2014 index file contains an error

It's not that hard to generate a csv file, but the csv index file for 2014 that is posted on amazon has had a mistake in it for the last 18 months. Hopefully this mistake will be fixed, but until then it generally needs a fix. 

One way is to just fix the file manually. 

Another is a perl one liner. The below fixes the file, but first backs up the original to index_2014.csv.bak

	$ perl -i.bak -p -e 's/SILVERCREST ASSET ,AMAGEMENT/SILVERCREST ASSET MANAGEMENT/g' index_2014.csv

We can see that it worked by diffing it.

	$ diff index_2014.csv index_2014.csv.bak
	39569c39569
	< 11146506,EFILE,136171217,201212,1/14/2014,MOSTYN FOUNDATION INC CO SILVERCREST ASSET MANAGEMENT,990PF,93491211007003,201302119349100700
	---
	> 11146506,EFILE,136171217,201212,1/14/2014,MOSTYN FOUNDATION INC CO SILVERCREST ASSET ,AMAGEMENT,990PF,93491211007003,201302119349100700 


# Yes the IRS has been told there's a problem

	
	---------- Forwarded message ----------
	From: jacob fenton <jsfenfen@gmail.com>
	Date: Wed, Oct 26, 2016 at 10:35 AM
	Subject: Re: MEF updates
	To: O'Reilly Sean E <Sean.E.OReilly@irs.gov>
		
	Hi Sean,
	
	I noticed that the index_2014.csv file is currently malformed--specifically, 
	the line that breaks the format contains a "taxpayer_name" of 
	MOSTYN FOUNDATION INC CO SILVERCREST ASSET ,AMAGEMENT. 
	Because CSV files use commas to delimit data, the internal comma "breaks" the file format.
	    
	That standard convention is to put quote marks around field values that include commas.
	    
	This occurs at approximately line number 39569 of the file index_2014.csv 
	-- the third line in what I've pasted below.
	    
	11146505,EFILE,830322736,201212,1/14/2014,CODY CHANGE ATTITUDES NOW INC,990PF,93491211006053,201302119349100605
	11146506,EFILE,136171217,201212,1/14/2014,MOSTYN FOUNDATION INC CO SILVERCREST ASSET ,AMAGEMENT,990PF,93491211007003,201302119349100700
	11146507,EFILE,840751642,201212,1/14/2014,RUTHERFORD FOUNDATION CO JAN HALL,990PF,93491211007053,201302119349100705
	    
	One "correct" way of representing this would be:
	    
	11146505,EFILE,830322736,201212,1/14/2014,CODY CHANGE ATTITUDES NOW INC,990PF,93491211006053,201302119349100605
	11146506,EFILE,136171217,201212,1/14/2014,"MOSTYN FOUNDATION INC CO SILVERCREST ASSET ,AMAGEMENT",990PF,93491211007003,201302119349100700
	11146507,EFILE,840751642,201212,1/14/2014,RUTHERFORD FOUNDATION CO JAN HALL,990PF,93491211007053,201302119349100705
	    
	--Jacob Fenton
	
	
asdf