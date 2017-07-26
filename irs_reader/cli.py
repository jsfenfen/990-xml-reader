import sys
import argparse
import json
from .filing import Filing
from .settings import KNOWN_SCHEDULES

def parse_args():

    parser = argparse.ArgumentParser("xirsx")

    parser.add_argument('object_ids', metavar='N', type=int, nargs='+',
                    help='object ids')

    parser.add_argument('--verbose', dest='verbose', action='store_const',
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

    args = parser.parse_args()
    return args


def main(args=None):
    """The main routine."""
    args_read = parse_args()

    for object_id in args_read.object_ids:
        if args_read.verbose:
            print("Processing filing %s" % object_id)
        this_filing = Filing(object_id)
        this_filing.process(verbose=args_read.verbose)
        if args_read.schedule:
            if args_read.format=='json':
                print(json.dumps(this_filing.get_schedule(args_read.schedule)))
            else:
                print(this_filing.get_schedule(args_read.schedule))
        else:
            if args_read.format=='json':
                print(json.dumps(this_filing.get_raw_irs_dict()))
            else:
                print(this_filing.get_raw_irs_dict())



if __name__ == "__main__":
    main()