import sys
import argparse
import json
import codecs
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

    parser.add_argument("--format",
        choices=['print', 'bare'],
        default='print',
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

def print_indented_json(data):
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        json.dump(data, sys.stdout, indent=2)
    else:
        json.dump(data, sys.stdout, indent=2)

def run_main(args_read):

    xml_runner = Runner()

    for object_id in args_read.object_ids:
        if args_read.verbose:
            print("Processing filing %s" % object_id)
        this_filing = Filing(object_id)
        this_filing.process(verbose=args_read.verbose)

        if args_read.list_schedules:
            print(this_filing.list_schedules())

        elif args_read.schedule:

            result = xml_runner.run_filing_single_schedule(object_id, args_read.schedule, verbose=args_read.verbose)
            if args_read.format=='bare':
                to_json(result, args_read.encoding)
            else:
                print_indented_json(result)
        else:
            result = xml_runner.run_filing(object_id, verbose=args_read.verbose)
            if args_read.format=='bare':
                to_json(result, args_read.encoding)
            else:
                print_indented_json(result)

def main(args=None):
    parser = get_parser()
    args_read = parser.parse_args()
    run_main(args_read)

if __name__ == "__main__":
    main()