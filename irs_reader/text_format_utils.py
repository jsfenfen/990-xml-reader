import json
import sys
import codecs
import re
import csv
import unicodecsv
 
from .standardizer import Standardizer, Documentizer, VersionDocumentizer


BRACKET_RE = re.compile(r'\[.*?\]')

ASTERISKS = "****************"

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

def to_json(data, outfilepath=None):
    if data:
        if outfilepath:
            with open(outfilepath, 'w') as outfile:
                json.dump(data, outfile)
        else:
            if hasattr(sys.stdout, "buffer"):
                sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
                json.dump(data, sys.stdout)
            else:
                json.dump(data, sys.stdout)

def to_csv(parsed_filing, object_id=None, standardizer=None, documentation=True, vd=None, outfilepath=None):
    if not vd:
        vd = VersionDocumentizer()
    stdout = getattr(sys.stdout, 'buffer', sys.stdout)
    if outfilepath:
        stdout = open(outfilepath, 'wb')  # or 'wb' ?

    fieldnames = []
    fieldnames = [ 
            'object_id', 'form', 'line_number', 'description', 'value', 'variable_name',
            'xpath', 'in_group', 'group_name', 'group_index'
        ]
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
                    this_result['variable_name'] = vardata['db_table'] + "." + vardata['db_name']

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
                this_result['object_id'] = object_id
                writer.writerow(this_result)


def to_txt(parsed_filing, standardizer=None, documentation=True, vd=None, outfilepath=None):
    if not vd:
        vd = VersionDocumentizer()
    results = parsed_filing.get_result()
    this_sked_name = None
    if outfilepath:
        outfile = open(outfilepath, 'w')
    if results:
        for result in results:
            for this_result in result['csv_line_array']:

                #### Collect the variables we need
                vardata = None
                textoutput = "\n"     # This is what we'll eventually write out
                this_result['form'] = this_result['xpath'].split("/")[1]
                try:
                    vardata = standardizer.get_var(this_result['xpath'])
                except KeyError:
                    pass
                if vardata:
                    this_result['variable_name'] = vardata['db_table'] + "." + vardata['db_name']

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
                    textoutput += "\n\n\n" + ASTERISKS + "\tSchedule %s\n" % this_result['form']
                    this_sked_name = this_result['form']
                
                textoutput += "\n" + ASTERISKS + "\n  Value: '%s'\nForm: %s\nLine:%s\nDescription:%s" % (
                    this_result['value'], 
                    this_result['form'],
                    this_result['line_number'],
                    this_result['description'], 
                )

                if documentation:
                    textoutput += "\nXpath:%s" % (this_result['xpath'])

                if this_result['in_group']:
                    textoutput += "\nGroup: %s group_index %s" % (
                        this_result['group_name'], 
                        this_result['group_index']
                    )
                else:
                    textoutput += "\nGroup:"
                    
                if outfilepath:
                    outfile.write(textoutput)
                else:
                    sys.stdout.write(textoutput)

    if outfilepath:
        outfile.close()