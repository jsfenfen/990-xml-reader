"""
Reads the .csv files and writes them back out in the project's "standard" csv format
Also removes "NA". 

Writes to FILENAME_standardformat.csv -- check the output is good before overwriting
"""

from .utils import get_group_writer, get_variable_writer, get_schedule_parts_writer, fix_row

import csv
 
if __name__ == '__main__':

    for filetype in ['groups', 'variables', 'schedule_parts']:
        INFILE = filetype + ".csv"
        OUTFILE = filetype + "_standardformat.csv"

        writer = None
        if filetype == 'groups':
           writer = get_group_writer(OUTFILE)
        elif filetype == 'variables':
           writer = get_variable_writer(OUTFILE)
        elif filetype == 'schedule_parts':
           writer = get_schedule_parts_writer(OUTFILE)


        infile = open(INFILE, 'r')
        reader = csv.DictReader(infile)
        for row in reader:
            result = fix_row(row)
            writer.writerow(result)

