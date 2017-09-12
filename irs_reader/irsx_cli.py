import argparse

from .filing import Filing
from .settings import KNOWN_SCHEDULES
from .runner import Runner
from .text_format_utils import to_json, print_documented_vars, \
    print_part_start, write_ordered_documentation, format_for_text


def get_parser():
    parser = argparse.ArgumentParser("irsx")

    parser.add_argument('object_ids',
                        metavar='object_ids',
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


def run_main(args_read):
    xml_runner = Runner(documentation=args_read.documentation)
    # Use the standardizer that was init'ed by Runner
    standardizer = xml_runner.get_standardizer()

    for object_id in args_read.object_ids:
        if args_read.verbose:
            print("Processing filing %s" % object_id)
        this_filing = Filing(object_id)
        this_filing.process(verbose=args_read.verbose)

        if args_read.list_schedules:
            print(this_filing.list_schedules())

        elif args_read.schedule:
            result = xml_runner.run_sked(object_id, args_read.schedule,
                                            verbose=args_read.verbose)
            if args_read.format == 'json':
                to_json(result, args_read.encoding)
            else:
                format_for_text(result, standardizer=standardizer,
                                documentation=args_read.documentation)
        else:
            result = xml_runner.run_filing(object_id,
                                        verbose=args_read.verbose)
            if args_read.format == 'json':
                to_json(result, args_read.encoding)
            else:
                format_for_text(result, standardizer=standardizer,
                                    documentation=args_read.documentation)


def main(args=None):
    parser = get_parser()
    args_read = parser.parse_args()
    run_main(args_read)

if __name__ == "__main__":
    main()
