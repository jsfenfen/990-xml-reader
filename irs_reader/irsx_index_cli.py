import sys
import argparse
from datetime import date
from .file_utils import get_index_file_URL, get_local_index_path, \
    stream_download

this_year = date.today().year
INDEXED_YEARS = [str(i) for i in range(2011, this_year+1)]


def get_cli_index_parser():
    parser = argparse.ArgumentParser("Irsreader")
    parser.add_argument(
        "--year",
        choices=INDEXED_YEARS,
        default=None,
        help='Optionally update an index file'
    )

    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_const',
        const=True, default=False,
        help='Verbose output'
    )
    return parser


def get_indexfile_by_year(year, verbose=False):
    localpath = get_local_index_path(year)
    remoteurl = get_index_file_URL(year)
    if verbose:
        print(
            "Getting index file for year: %s remote=%s local=%s"
            % (year, remoteurl, localpath)
        )
    stream_download(remoteurl, localpath, verbose=verbose)


def run_cli_index_main(args_read):
    if args_read.year:
        get_indexfile_by_year(args_read.year, verbose=args_read.verbose)
    else:
        for year in INDEXED_YEARS:
            get_indexfile_by_year(year, verbose=args_read.verbose)


def main(args=None):
    parser = get_cli_index_parser()
    args = parser.parse_args()
    run_cli_index_main(args)


if __name__ == "__main__":
    main()
