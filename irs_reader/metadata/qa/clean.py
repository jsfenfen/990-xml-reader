"""
Reads the concordance file and writes it back out in the project's "standard" csv format
https://github.com/Nonprofit-Open-Data-Collective/irs-efile-master-concordance-file/tree/master/qa
Also removes "NA". Historically these had been included, though should be gone by now. 

Writes to efiler_master_concordance_reformatted.csv -- check the output is good before overwriting
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

