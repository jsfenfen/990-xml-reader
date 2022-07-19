import sys
import os
import argparse
from zipfile import ZipFile
from .file_utils import stream_download
from .settings import WORKING_DIRECTORY

IRS_location = "https://apps.irs.gov/pub/epostcard/990/xml/%s/download990xml_%s"

ref_url = "https://www.irs.gov/charities-non-profits/form-990-series-downloads"
# How many files are available per year? 
# https://www.irs.gov/charities-non-profits/form-990-series-downloads
number_of_files = {
    '2022':0,
    '2021':6,
    '2020':8,
    '2019':8,
    '2018':7,
    '2017':7,
    '2016':6,
    '2015':2
}

def get_cli_retrieve_parser():
    parser = argparse.ArgumentParser("Irsreader")
    parser.add_argument(
        "year",
        nargs='+',
        help='4-digit year to retrieve, '
    )

    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_const',
        const=True, default=False,
        help='Verbose output'
    )
    return parser


def download_unzip_erase(remote_url, verbose=False):
    local_name = remote_url.split("/")[-1]
    local_path = os.path.join(WORKING_DIRECTORY, local_name)

    if verbose:
        print("Downloading %s to %s" % (remote_url, local_path))
    stream_download(remote_url, local_path, verbose=verbose)

    with ZipFile(local_path, 'r') as zipObj:
    # Extract all the contents of zip file in different directory
        print('Unzipping %s to %s' % (local_path, WORKING_DIRECTORY))
        zipObj.extractall(WORKING_DIRECTORY)

    print("Cleaning up, removing raw file.")
    os.remove(local_path)

def unload_zipfile_by_year(year, verbose=False):
    print("Retrieving zipfiles for year %s" % year)
    if verbose:
        print("Running verbose")

    num_files = number_of_files[year]
    location_base = IRS_location % (year, year)
    file_list = []

    if num_files == 0:
        file_list.append(location_base + ".zip")

    if num_files > 0:
        for i in range(1, num_files+1):
            file_list.append(location_base + "_" + str(i) + ".zip")

    for this_file in file_list:
        download_unzip_erase(this_file, verbose=verbose)


def run_cli_retrieve_main(args_read):
    print("""
    Please visit https://www.irs.gov/charities-non-profits/form-990-series-downloads
    To see if any additional files are available. 
    """)
    for year in args_read.year:
        print("Processing %s files for year %s" % (year, number_of_files[year]))
        unload_zipfile_by_year(year, verbose=args_read.verbose)

def main(args=None):
    parser = get_cli_retrieve_parser()
    args = parser.parse_args()
    run_cli_retrieve_main(args)

if __name__ == "__main__":
    main()