import argparse

from .filing import Filing
from .settings import KNOWN_SCHEDULES, IRS_READER_ROOT
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
        "--xpath",
        dest='documentation',
        action='store_const',
        const=True, default=False,
        help='show xpath in text format'
    )
    parser.add_argument(
        "--format",
        choices=['json', 'csv', 'txt'],
        default='json',
        help='Output format'
    )
    parser.add_argument(
        "--file",
        default=None,
        help='Write result to file'
    )
    parser.add_argument(
        '--list_schedules',
        dest='list_schedules',
        action='store_const',
        const=True,
        default=False,
        help='Only list schedules'
    )
    parser.add_argument(
        '--input-dir',
        dest='input_dir',
        default=None,
        help='Directory to find XML files (overrides default working directory)'
    )
    return parser


def run_main(args_read):

    # If --input-dir is provided, make it authoritative: override the
    # settings-derived working directory so any code path that still reads
    # it (e.g. get_local_path) points at the user-supplied directory.
    if args_read.input_dir:
        from . import settings as _irsx_settings
        from . import file_utils as _irsx_file_utils
        _irsx_settings.WORKING_DIRECTORY = args_read.input_dir
        _irsx_file_utils.WORKING_DIRECTORY = args_read.input_dir

    csv_format = args_read.format == 'csv' or args_read.format == 'txt'
    xml_runner = XMLRunner(
        documentation=args_read.documentation,
        csv_format=csv_format
    )

    # Use the standardizer that was init'ed by XMLRunner
    standardizer = xml_runner.get_standardizer()

    for object_id in args_read.object_ids:
        if args_read.verbose:
            print("Processing filing %s" % object_id)
            if args_read.file:
                print("Printing result to file %s" % args_read.file)

        # Build filepath from --input-dir if provided
        filepath = None
        if args_read.input_dir:
            import os
            filepath = os.path.join(args_read.input_dir, "%s_public.xml" % object_id)

        if args_read.list_schedules:
            this_filing = Filing(object_id, filepath=filepath)
            this_filing.process()
            print(this_filing.list_schedules())
            return True  # we're done, ignore any other commands

        else:
            if args_read.schedule:
                parsed_filing = xml_runner.run_sked(
                    object_id,
                    args_read.schedule,
                    verbose=args_read.verbose,
                    filepath=filepath
                )
            else:
                parsed_filing = xml_runner.run_filing(
                    object_id,
                    verbose=args_read.verbose,
                    filepath=filepath
                )

        if args_read.format == 'json':
            to_json(parsed_filing.get_result(), outfilepath=args_read.file)

        elif args_read.format == 'csv':
                to_csv(
                    parsed_filing,
                    object_id=object_id,
                    standardizer=standardizer,
                    documentation=args_read.documentation,
                    outfilepath=args_read.file
                )

        elif args_read.format == 'txt':
                to_txt(
                    parsed_filing,
                    standardizer=standardizer,
                    documentation=args_read.documentation,
                    outfilepath=args_read.file
                )


def main(args=None):
    parser = get_parser()
    args_read = parser.parse_args()
    run_main(args_read)
    print("\n")

if __name__ == "__main__":
    main()
