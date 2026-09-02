"""
Download IRS 990 XML filings in bulk.

Supports two sources:
  - IRS TEOS bulk download site (2019-present): scrapes the IRS downloads page
    to discover zip files, then downloads and extracts them.
  - Internet Archive (2010-2019): downloads tar.gz archives from archive.org.

Usage:
    irsx_retrieve irs 2023 2024
    irsx_retrieve irs 2024 --output-dir ./xml/2024
    irsx_retrieve irs 2024 --index-only
    irsx_retrieve archive 2015 2016
    irsx_retrieve archive 2015 --output-dir ./xml/2015
"""
import sys
import os
import re
import io
import argparse
import tarfile
import time
from zipfile import ZipFile
from .file_utils import stream_download
from .settings import WORKING_DIRECTORY

IRS_DOWNLOADS_PAGE = "https://www.irs.gov/charities-non-profits/form-990-series-downloads"
IRS_BASE_URL = "https://apps.irs.gov/pub/epostcard/990/xml"
ARCHIVE_BASE_URL = "https://archive.org/download/IRS990-efile"


# ── IRS download helpers ─────────────────────────────────────────────────


def discover_zip_urls(year, verbose=False):
    """Scrape the IRS downloads page to find all zip URLs for a given year."""
    import requests

    if verbose:
        print("Discovering zip files for %s from IRS downloads page..." % year)

    resp = requests.get(IRS_DOWNLOADS_PAGE, timeout=30)
    resp.raise_for_status()
    html = resp.text

    year_str = str(year)
    urls = []
    for match in re.finditer(r'href="([^"]*)"', html):
        url = match.group(1)
        if url.endswith('.zip') and ('/%s/' % year_str) in url:
            if url.startswith('http'):
                full_url = url
            else:
                full_url = 'https://apps.irs.gov' + url
            if full_url not in urls:
                urls.append(full_url)

    if verbose:
        print("Found %d zip files for %s" % (len(urls), year))

    return urls


def download_index(year, output_dir, verbose=False):
    """Download the index CSV for a given year."""
    import requests

    url = "%s/%s/index_%s.csv" % (IRS_BASE_URL, year, year)
    if verbose:
        print("Fetching index: %s" % url)

    resp = requests.get(url, timeout=30)
    if resp.status_code in (404, 302):
        print("No index file found for %s" % year)
        return None

    resp.raise_for_status()

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "index_%s.csv" % year)
    with open(out_path, 'w') as f:
        f.write(resp.text)
    print("Index saved to %s" % out_path)
    return out_path


def download_and_extract_zip(url, output_dir, verbose=False):
    """Download a zip file, extract XML files, and remove the zip."""
    import requests

    local_name = url.split("/")[-1]
    local_path = os.path.join(output_dir, local_name)

    if verbose:
        print("Downloading %s" % url)
    stream_download(url, local_path, verbose=verbose)

    count = 0
    skipped = 0
    with ZipFile(local_path, 'r') as zipObj:
        xml_names = [n for n in zipObj.namelist() if n.endswith('.xml')]
        for name in xml_names:
            filename = name.split('/')[-1]
            out_path = os.path.join(output_dir, filename)
            if os.path.exists(out_path):
                skipped += 1
                continue
            zipObj.extract(name, output_dir)
            count += 1

    os.remove(local_path)
    return count, skipped


def download_year_irs(year, output_dir, index_only=False, verbose=False):
    """Download all zip files for a year from the IRS."""
    year_str = str(year)
    os.makedirs(output_dir, exist_ok=True)

    if index_only:
        download_index(year_str, output_dir, verbose=verbose)
        return

    urls = discover_zip_urls(year_str, verbose=verbose)

    if not urls:
        print("No zip files found for %s on the IRS downloads page." % year_str)
        print("Check %s" % IRS_DOWNLOADS_PAGE)
        return

    total = 0
    total_skipped = 0
    for url in urls:
        filename = url.split('/')[-1]
        print("  %s ..." % filename, end=' ', flush=True)
        try:
            count, skipped = download_and_extract_zip(
                url, output_dir, verbose=verbose
            )
            print("%d extracted, %d skipped" % (count, skipped))
            total += count
            total_skipped += skipped
        except Exception as e:
            print("error: %s" % e)

        # Be polite to the IRS servers
        time.sleep(0.5)

    print("\nDone. %d extracted, %d skipped for %s in %s" % (
        total, total_skipped, year_str, output_dir
    ))


# ── Internet Archive download helpers ────────────────────────────────────


def download_year_archive(year, output_dir, verbose=False):
    """Download and extract a year's tar.gz from the Internet Archive.

    Available years: 2010-2019.
    URL pattern: https://archive.org/download/IRS990-efile/irs_form990_xml.{YEAR}.tar.gz
    """
    import requests

    year_int = int(year)
    if year_int < 2010 or year_int > 2019:
        print("Internet Archive source only has years 2010-2019, got %s" % year)
        return

    url = "%s/irs_form990_xml.%s.tar.gz" % (ARCHIVE_BASE_URL, year)
    os.makedirs(output_dir, exist_ok=True)

    print("Downloading %s ..." % url)
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()

    content_length = resp.headers.get('Content-Length')
    if content_length:
        print("  Size: %.1f MB" % (int(content_length) / 1048576.0))

    # Download into memory, then extract (files are 11MB-2.1GB)
    print("  Downloading...", flush=True)
    data = resp.content
    print("  Downloaded %.1f MB, extracting..." % (len(data) / 1048576.0))

    count = 0
    skipped = 0

    fileobj = io.BytesIO(data)
    with tarfile.open(fileobj=fileobj, mode='r:gz') as tar:
        for member in tar:
            if not member.name.endswith('.xml'):
                continue

            filename = member.name.split('/')[-1]
            out_path = os.path.join(output_dir, filename)

            if os.path.exists(out_path):
                skipped += 1
            else:
                # Extract to a temp name then rename, to handle directory
                # prefixes in the tar
                extracted = tar.extractfile(member)
                if extracted is None:
                    continue
                with open(out_path, 'wb') as f:
                    f.write(extracted.read())
                count += 1

            if (count + skipped) % 10000 == 0:
                print("  %d extracted, %d skipped..." % (count, skipped))

    print("  %d extracted, %d skipped (already existed)" % (count, skipped))


# ── CLI ──────────────────────────────────────────────────────────────────


def get_cli_retrieve_parser():
    parser = argparse.ArgumentParser(
        "irsx_retrieve",
        description="Download IRS 990 XML filings in bulk."
    )
    subparsers = parser.add_subparsers(dest='source', required=True)

    # irsx_retrieve irs <years>
    irs_parser = subparsers.add_parser(
        'irs',
        help='Download from IRS TEOS bulk download site (2019-present)'
    )
    irs_parser.add_argument(
        'year', nargs='+',
        help='4-digit year(s) to retrieve'
    )
    irs_parser.add_argument(
        '--output-dir', default=None,
        help='Output directory (default: IRSX_WORKING_DIRECTORY)'
    )
    irs_parser.add_argument(
        '--index-only', action='store_true', default=False,
        help='Only download the index CSV, skip zip files'
    )
    irs_parser.add_argument(
        '--verbose', action='store_true', default=False,
        help='Verbose output'
    )

    # irsx_retrieve archive <years>
    archive_parser = subparsers.add_parser(
        'archive',
        help='Download from Internet Archive (2010-2019)'
    )
    archive_parser.add_argument(
        'year', nargs='+',
        help='4-digit year(s) to retrieve (2010-2019)'
    )
    archive_parser.add_argument(
        '--output-dir', default=None,
        help='Output directory (default: IRSX_WORKING_DIRECTORY)'
    )
    archive_parser.add_argument(
        '--verbose', action='store_true', default=False,
        help='Verbose output'
    )

    return parser


def run_cli_retrieve_main(args):
    output_dir = args.output_dir or WORKING_DIRECTORY

    if args.source == 'irs':
        for year in args.year:
            download_year_irs(
                year, output_dir,
                index_only=args.index_only,
                verbose=args.verbose
            )
    elif args.source == 'archive':
        for year in args.year:
            download_year_archive(year, output_dir, verbose=args.verbose)


def main(args=None):
    parser = get_cli_retrieve_parser()
    args = parser.parse_args(args)
    run_cli_retrieve_main(args)


if __name__ == "__main__":
    main()
