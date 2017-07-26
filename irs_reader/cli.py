import sys
import argparse
from datetime import date
from .file_utils import get_index_file_URL, get_local_index_path, \
    stream_download

this_year = date.today().year
INDEXED_YEARS = [str(i) for i in range(2010, this_year+1)]

def parse_args():

    parser = argparse.ArgumentParser("Irsreader")
    
    parser.add_argument("--updateindex",
        choices=INDEXED_YEARS,
        default=None,
        help='Optionally update an index file')

    parser.add_argument('--getindexes', dest='getindexes', action='store_const',
                    const=True, default=False,
                    help='Optionally get all index files')

    parser.add_argument('--verbose', dest='verbose', action='store_const',
                    const=True, default=False,
                    help='Verbose output')

    args = parser.parse_args()
    return args

def get_indexfile_by_year(year, verbose=False):
    print("Getting index file for year: %s" % year)

    localpath = get_local_index_path(year)
    remoteurl = get_index_file_URL(year)
    stream_download(remoteurl, localpath, verbose=verbose)

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    args_read = parse_args()
    if args_read.getindexes:
        for year in INDEXED_YEARS:  
            get_indexfile_by_year(year, verbose=args_read.verbose)
    elif args_read.updateindex:
        get_indexfile_by_year(args_read.updateindex, verbose=args_read.verbose)

if __name__ == "__main__":
    main()