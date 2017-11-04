import json
import sys
import codecs
import re
import csv
import unicodecsv
 
from .standardizer import Standardizer, Documentizer, VersionDocumentizer


BRACKET_RE = re.compile(r'\[.*?\]')


def debracket(string):
    """ Eliminate the bracketed var names in doc, line strings """
    result = re.sub(BRACKET_RE, ';', str(string))
    result = result.lstrip(';')
    result = result.lstrip(' ')
    result = result.replace('; ;',';')
    return result

def most_recent(semicolon_delimited_string):
    result = semicolon_delimited_string.split(";")[-1]
    return result


def to_json(data):
    if data:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
            json.dump(data, sys.stdout)
        else:
            json.dump(data, sys.stdout)

"""
def print_documented_vars(vardata):
    var_array = []
    for this_key in vardata.keys():
        if this_key == 'name':
            continue
        this_var = vardata[this_key]
        this_var['name'] = this_key
        var_array.append(this_var)
    sorted_vars = sorted(var_array, key=lambda k: int(k['ordering']))

    for this_vardata in sorted_vars:
        print("\n\t*%s*: value=%s \n\tLine '%s' Desc: '%s' Type: %s" % (
            this_vardata['name'],
            this_vardata['value'],
            this_vardata.get('line_number') or '',
            this_vardata.get('description') or '',
            this_vardata.get('db_type') or '')
        )


def print_part_start(part_name):
    print("\n%s\n" % part_name)


def write_ordered_documentation(data, standardizer):
    for schedule in data:
        print("\nSchedule: %s\n" % schedule['schedule_name'])
        schedule_parts = []
        for key in schedule['schedule_parts'].keys():
            this_part = schedule['schedule_parts'][key]
            this_part['name'] = key
            schedule_parts.append(this_part)

        schedule_parts_sorted = sorted(
            schedule_parts,
            key=lambda k: standardizer.part_ordering(k['name']))

        for part in schedule_parts_sorted:
            print_part_start(part['name'])
            print_documented_vars(part)

        for grpkey in schedule['groups'].keys():
            for grp in schedule['groups'][grpkey]:
                print ("\nRepeating Group: %s\n" % grpkey)

                print_documented_vars(grp)
"""

def to_csv(parsed_filing, standardizer=None, documentation=True, vd=None, csvfilepath=None):
    if not vd:
        vd = VersionDocumentizer()

    stdout = getattr(sys.stdout, 'buffer', sys.stdout)

    if csvfilepath:
        stdout = open(csvfilepath, 'w')  # or 'wb' ?

    fieldnames = []
    if documentation:
        fieldnames = [ 
            'form', 'line_number', 'description', 'value', 'variable_name',
            'xpath', 'in_group', 'group_name', 'group_index'
        ]
    else:
        fieldnames = [ 
            'value', 'xpath', 'variable_name', 'in_group', 'group_name', 'group_index'
        ]

    header = ",".join(fieldnames)
    print(header)

    #   unicodecsv
    writer = unicodecsv.DictWriter(
        stdout,
        fieldnames=fieldnames,
        encoding='utf-8',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()   # this fails in python3? 
    results = parsed_filing.get_result()

    if results:
        for result in results:
            for this_result in result['csv_line_array']:

                vardata = None
                try:
                    vardata = standardizer.get_var(this_result['xpath'])
                except KeyError:
                    pass
                if vardata:
                    this_result['variable_name'] = vardata['db_table'] + "__" + vardata['db_name']

                if documentation:     # not sure why you'd want a csv without docs?
                    raw_line_num = vd.get_line_number(
                        this_result['xpath'], 
                        parsed_filing.get_version()
                    )
                    this_result['line_number'] =  debracket(raw_line_num)

                    raw_description = vd.get_description(
                        this_result['xpath'], 
                        parsed_filing.get_version()
                    )
                    this_result['description'] =  debracket(raw_description)
                    this_result['form'] = this_result['xpath'].split("/")[1]
                writer.writerow(this_result)


def to_txt(parsed_filing, standardizer=None, documentation=True, vd=None):
    if not vd:
        vd = VersionDocumentizer()
    results = parsed_filing.get_result()
    this_sked_name = None

    for result in results:
        for this_result in result['csv_line_array']:

            #### Collect the variables we need
            vardata = None
            textoutput = ""     # This is what we'll eventually write out
            this_result['form'] = this_result['xpath'].split("/")[1]
            try:
                vardata = standardizer.get_var(this_result['xpath'])
            except KeyError:
                pass
            if vardata:
                this_result['variable_name'] = vardata['db_table'] + "__" + vardata['db_name']

            if documentation:     # not sure why you'd want a csv without docs?
                raw_line_num = vd.get_line_number(
                    this_result['xpath'], 
                    parsed_filing.get_version()
                )
                this_result['line_number'] =  debracket(raw_line_num)

                raw_description = vd.get_description(
                    this_result['xpath'], 
                    parsed_filing.get_version()
                )
                this_result['description'] =  debracket(raw_description)

            #### Write the output, now that we've got the vars 

            if this_sked_name != this_result['form']:
                textoutput += "\n\n\tSchedule %s\n" % this_result['form']
                this_sked_name = this_result['form']
            
            if documentation:
                textoutput += "\nForm %s Line:%s Description:%s\nValue=%s" % (
                    this_result['form'], 
                    this_result['line_number'], 
                    this_result['description'], 
                    this_result['value'], 
                )
                if this_result['in_group']:
                    textoutput += "\nGroup: %s group_index %s" % (this_result['group_name'], this_result['group_index'])
                else:
                    textoutput += "\nGroup:"
            else:
                textoutput += "\nValue:%s xpath:%s " % (this_result['value'], this_result['xpath'])
                if this_result['in_group']:
                    textoutput += "Group: %s group_index %s" % (this_result['group_name'], this_result['group_index'])
            print(textoutput)
