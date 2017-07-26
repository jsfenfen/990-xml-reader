import sys
import argparse
from datetime import date
from .file_utils import get_index_file_URL, get_local_index_path, \
    stream_download

this_year = date.today().year
INDEXED_YEARS = [str(i) for i in range(2010, this_year+1)]

def parse_args():

    parser = argparse.ArgumentParser("Irsreader")

    parser.add_argument('--verbose', dest='verbose', action='store_const',
                    const=True, default=False,
                    help='Verbose output')

    args = parser.parse_args()
    return args


def main(args=None):
    """The main routine."""
    args_read = parse_args()


if __name__ == "__main__":
    main()