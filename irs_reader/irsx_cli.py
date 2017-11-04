import argparse

from .filing import Filing
from .settings import KNOWN_SCHEDULES
from .xmlrunner import XMLRunner
from .text_format_utils import * 

def get_parser():
    parser = argparse.ArgumentParser("irsx")

    parser.add_argument(
        'object_ids',
        metavar='object_ids',
        type=int,
        nargs='+',
        help='object ids'
    )
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_const',
        const=True, default=False,
        help='Verbose output'
    )
    parser.add_argument(
        "--schedule",
        choices=KNOWN_SCHEDULES,
        default=None,
        help='Get only that schedule'
    )
    parser.add_argument(
        "--no_doc",
        dest='documentation',
        action='store_const',
        const=False, default=True,
        help='Hide line number, description, other documentation'
    )
    parser.add_argument(
        "--format",
        choices=['json', 'csv', 'txt'],
        default='json',
        help='Output format'
    )
    parser.add_argument(
        '--list_schedules',
        dest='list_schedules',
        action='store_const',
        const=True,
        default=False,
        help='Only list schedules'
    )
    #### Do we really wanna claim to support encodings... 
    #parser.add_argument(
    #    "--encoding",
    #    default="utf-8",
    #    help="encoding (probably utf-8)"
    #)
    return parser


def run_main(args_read):

    csv_format= args_read.format=='csv' or args_read.format=='txt'
    xml_runner = XMLRunner(documentation=args_read.documentation, csv_format=csv_format)

    # Use the standardizer that was init'ed by XMLRunner
    standardizer = xml_runner.get_standardizer()

    for object_id in args_read.object_ids:
        if args_read.verbose:
            print("Processing filing %s" % object_id)

        if args_read.list_schedules:
            this_filing = Filing(object_id)
            this_filing.process()
            print(this_filing.list_schedules())

        else:
            if args_read.schedule:
                parsed_filing = xml_runner.run_sked(
                    object_id,
                    args_read.schedule,
                    verbose=args_read.verbose
                )
            else:
                parsed_filing = xml_runner.run_filing(
                    object_id,
                    verbose=args_read.verbose
                )

        if args_read.format == 'json':
            to_json(parsed_filing.get_result())

        elif args_read.format=='csv':   
                to_csv(
                    parsed_filing,
                    standardizer=standardizer,
                    documentation=args_read.documentation,
                )

        elif args_read.format=='txt':
                to_txt(
                    parsed_filing,
                    standardizer=standardizer,
                    documentation=args_read.documentation,
                )


def main(args=None):
    parser = get_parser()
    args_read = parser.parse_args()
    run_main(args_read)

if __name__ == "__main__":
    main()
