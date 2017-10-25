import csv

# field names for 'variables.csv' file
VARIABLE_FIELDNAMES = [
    'parent_sked', 'parent_sked_part', 'in_a_group', 'db_table', 'ordering',
    'db_name', 'xpath', 'irs_type', 'db_type', 'line_number', 'description',
    'versions'
]

GROUP_FIELDNAMES = [
    'parent_sked', 'parent_sked_part', 'ordering', 'xpath', 'db_name',
    'line_number', 'description', 'headless', 'versions'
]

SCHEDULE_PART_FIELDNAMES = [
    'parent_sked', 'parent_sked_part', 'ordering', 
    'part_name', 'xml_root', 'is_shell'
]

# concordance file from nonprofit data coalition, working on 'interoperability' with their standards (which we've helped in)
NDC_FIELDNAMES = [
    'variable_name', 'description', 'scope', 'location_code', 'form', 'part',
    'data_type', 'required', 'cardinality', 'rdb_table', 'xpath', 'version',
    'production_rule', 'last_version_modified'
]

def get_writer(outfilename, fieldnames):
    """ Returns a writer that writes to the csv 'spec' we use
        Keeping files consistent makes file diffs more readable.
    """
    outfile = open(outfilename, 'w') # 'wb' python 2?
    writer = csv.DictWriter(
        outfile,
        fieldnames=fieldnames,
        delimiter=',',
        quotechar='"',
        lineterminator='\n',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()
    return writer

def get_variable_writer(outfilename):
    return get_writer(outfilename, VARIABLE_FIELDNAMES)

def get_group_writer(outfilename):
    return get_writer(outfilename, GROUP_FIELDNAMES)

def get_schedule_parts_writer(outfilename):
    return get_writer(outfilename, SCHEDULE_PART_FIELDNAMES)

def get_ndc_writer(outfilename):
    return get_writer(outfilename, NDC_FIELDNAMES)

def clean_value(value):
    """ This gets run on every value """
    value = value.lstrip(" ")     # Remove leading whitespace
    if value=='NA':               # Throw out NA's
        return ''
    return value

def fix_row(rowdict):
    for key in rowdict.keys():
        rowdict[key] = clean_value(rowdict[key])
    return rowdict