import sys
import argparse
import json
import codecs
from .filing import Filing
from .settings import KNOWN_SCHEDULES

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
        choices=['dict', 'json'],
        default='dict',
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

###
def run_main(args_read):
    for object_id in args_read.object_ids:
        if args_read.verbose:
            print("Processing filing %s" % object_id)
        this_filing = Filing(object_id)
        this_filing.process(verbose=args_read.verbose)

        if args_read.list_schedules:
            print(this_filing.list_schedules())

        elif args_read.schedule:

            if args_read.format=='json':
                to_json( this_filing.get_schedule(args_read.schedule), 
                    args_read.encoding )
            else:
                print(this_filing.get_schedule(args_read.schedule) )
        else:
            if args_read.format=='json':
                to_json( this_filing.get_raw_irs_dict(), args_read.encoding )
            else:
                print(this_filing.get_raw_irs_dict() )

def main(args=None):
    parser = get_parser()
    args_read = parser.parse_args()
    run_main(args_read)

if __name__ == "__main__":
    main()