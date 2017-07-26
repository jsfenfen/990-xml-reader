import sys
import argparse
from datetime import date
from .file_utils import get_index_file_URL, get_local_index_path, \
    stream_download

this_year = date.today().year
INDEXED_YEARS = [str(i) for i in range(2010, this_year+1)]

def parse_args():

    parser = argparse.ArgumentParser("Irsreader")
    parser.add_argument("--year",
        choices=INDEXED_YEARS,
        default=None,
        help='Optionally update an index file')

    parser.add_argument('--verbose', dest='verbose', action='store_const',
                const=True, default=False,
                help='Verbose output')

    args = parser.parse_args()
    return args

def get_indexfile_by_year(year, verbose=False):
    if verbose:
        print("Getting index file for year: %s" % year)
    localpath = get_local_index_path(year)
    remoteurl = get_index_file_URL(year)
    stream_download(remoteurl, localpath, verbose=verbose)

def main(args=None):
    """The main routine."""
    args_read = parse_args()

    if args_read.year:
        get_indexfile_by_year(args_read.year, verbose=args_read.verbose)
    else:
        for year in INDEXED_YEARS:  
            get_indexfile_by_year(year, verbose=args_read.verbose)


if __name__ == "__main__":
    main()