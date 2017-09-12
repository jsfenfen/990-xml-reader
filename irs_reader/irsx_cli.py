import sys
import argparse
import json
import codecs
from operator import itemgetter
from .filing import Filing
from .settings import KNOWN_SCHEDULES
from .runner import Runner

def get_parser():
    parser = argparse.ArgumentParser("xirsx")

    parser.add_argument('object_ids', 
        metavar='N', 
        type=int, 
        nargs='+',
        help='object ids')

    parser.add_argument('--verbose', 
        dest='verbose', 
        action='store_const',
        const=True, default=False,
        help='Verbose output')

    parser.add_argument("--schedule",
        choices=KNOWN_SCHEDULES,
        default=None,
        help='Get only that schedule')

    parser.add_argument("--documentation",
        dest='documentation',
        action='store_const',
        const=True, default=False,
        help='Show documentation with output')

    parser.add_argument("--format",
        choices=['json', 'txt'],
        default='json',
        help='Output format')

    parser.add_argument('--list_schedules', 
        dest='list_schedules', 
        action='store_const', 
        const=True, 
        default=False,
        help='Only list schedules')

    parser.add_argument("--encoding",
        default="utf-8",
        help="encoding (probably utf-8)")

    return parser
   
### Thanks to github.com/jsvine/pdfplumber see cli.py#L11 
class DecimalEncoder(json.JSONEncoder):
    """ 
    Helper to deal with decimal encoding, think it's not needed here now(?)
    """
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o.quantize(Decimal('.0001'), rounding=ROUND_HALF_UP))
        return super(DecimalEncoder, self).default(o)
### ibid.
def to_json(data, encoding=None):
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        json.dump(data, sys.stdout)
    else:
        json.dump(data, sys.stdout)


def print_documented_vars(vardata):
    var_array = []
    for this_key in vardata.keys():
        if this_key=='name':
            continue
        this_var = vardata[this_key]
        this_var['name'] = this_key
        var_array.append(this_var)
    sorted_vars = sorted(var_array, key=lambda k: int(k['ordering'])) 

    for this_vardata in sorted_vars:
        print("\n\t*%s*: value=%s \n\tLine Number '%s' Description: '%s' Type: %s" % (this_vardata['name'], this_vardata['value'], this_vardata.get('line_number') or '', this_vardata.get('description') or '' , this_vardata.get('db_type') or ''))

def print_part_start(part_name):
    print("\n%s\n" % part_name)

def write_ordered_documentation(data, standardizer):

    for schedule in data:
        print("\nSchedule: %s\n" % schedule['schedule_name'])

        schedule_parts = []
        for key in schedule['data']['schedule_parts'].keys():
            this_part = schedule['data']['schedule_parts'][key]
            this_part['name']=key

            schedule_parts.append(this_part)

        schedule_parts_sorted = sorted(schedule_parts, key=lambda k: standardizer.part_ordering(k['name']))
        for part in schedule_parts_sorted:
            print_part_start(part['name'])
            print_documented_vars(part)
        
        for grpkey in schedule['data']['groups'].keys():
            for grp in schedule['data']['groups'][grpkey]:
                print ("\nRepeating Group: %s\n" % grpkey)

                print_documented_vars(grp)


def format_for_text(data, standardizer=None, documentation=False):
    """ If we're not showing documentation, just pretty print the json
        But if we're showing the documentation, reorder it.
    """
    if documentation:
        if not standardizer:
            raise Exception("standardizer must be included to order documentation")
        write_ordered_documentation(data, standardizer)

    else:    
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
            json.dump(data, sys.stdout, indent=4)
        else:
            json.dump(data, sys.stdout, indent=4)
    
    print("\n\n")

def run_main(args_read):

    xml_runner = Runner(documentation=args_read.documentation)
    # Use the same standardizer we already created
    standardizer = xml_runner.get_standardizer()

    for object_id in args_read.object_ids:
        if args_read.verbose:
            print("Processing filing %s" % object_id)
        this_filing = Filing(object_id)
        this_filing.process(verbose=args_read.verbose)

        if args_read.list_schedules:
            print(this_filing.list_schedules())

        elif args_read.schedule:
            result = xml_runner.run_filing_single_schedule(object_id, args_read.schedule, verbose=args_read.verbose)

            if args_read.format=='json':
                to_json(result, args_read.encoding)
            else:
                format_for_text(result, standardizer=standardizer, documentation=args_read.documentation)
        else:

            result = xml_runner.run_filing(object_id, verbose=args_read.verbose)
            if args_read.format=='json':
                to_json(result, args_read.encoding)
            else:
                format_for_text(result, standardizer=standardizer, documentation=args_read.documentation)

def main(args=None):
    parser = get_parser()
    args_read = parser.parse_args()
    run_main(args_read)

if __name__ == "__main__":
    main()