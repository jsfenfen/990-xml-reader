import sys
import argparse
import json
import codecs
from .filing import Filing
from .settings import KNOWN_SCHEDULES

def parse_args():
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

    args = parser.parse_args()
    return args

class DecimalEncoder(json.JSONEncoder):
    """ Thanks to github.com/jsvine/pdfplumber see cli.py#L11 """
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o.quantize(Decimal('.0001'), rounding=ROUND_HALF_UP))
        return super(DecimalEncoder, self).default(o)

def to_json(data, encoding):
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        json.dump(data, sys.stdout, cls=DecimalEncoder)
    else:
        json.dump(data, sys.stdout, cls=DecimalEncoder, encoding=encoding)

def main(args=None):
    """The main routine."""
    args_read = parse_args()

    for object_id in args_read.object_ids:
        if args_read.verbose:
            print("Processing filing %s" % object_id)
        this_filing = Filing(object_id)
        this_filing.process(verbose=args_read.verbose)

        if args_read.list_schedules:
            print(this_filing.get_schedules())

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

if __name__ == "__main__":
    main()