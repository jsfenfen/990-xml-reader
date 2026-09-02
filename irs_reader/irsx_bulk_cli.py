"""
Bulk parse all XML files in a directory, in parallel.

Loads the Standardizer once per worker process via the pool initializer,
then reuses it for every filing that worker handles.

Usage:
    irsx_bulk /path/to/xml --output-dir /path/to/output
    irsx_bulk --year 2024 --output-dir /path/to/output
    irsx_bulk /path/to/xml --output-dir /path/to/output --format jsonl
    irsx_bulk /path/to/xml --output-dir /path/to/output --skip-existing
    irsx_bulk /path/to/xml --output-dir /path/to/output --limit 500
"""
import argparse
import csv
import glob
import json
import os
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

from .filing import Filing, InvalidXMLException, FileMissingException
from .settings import version_is_supported, WORKING_DIRECTORY
from .standardizer import Standardizer
from .sked_dict_reader import SkedDictReader
from .type_utils import listType

# Per-worker process globals, set by _init_worker
_standardizer = None
_group_dicts = None


def _init_worker():
    """Called once when each worker process starts."""
    global _standardizer, _group_dicts
    _standardizer = Standardizer()
    _group_dicts = _standardizer.get_groups()


def _parse_filing(filepath):
    """Parse a single filing and return the structured data plus keyerrors."""
    filename = os.path.basename(filepath)
    object_id = filename.replace('_public.xml', '')

    try:
        filing = Filing(object_id, filepath=filepath)
        filing.process()
    except (InvalidXMLException, FileMissingException, Exception) as e:
        return {'file': filename, 'object_id': object_id, 'error': str(e)}

    version = filing.get_version()
    if not version_is_supported(version):
        return {'file': filename, 'object_id': object_id,
                'error': 'Unsupported version: %s' % version}

    ein = filing.get_ein()
    whole_filing_data = []
    keyerrors = []
    group_keyerrors = []

    for sked in filing.list_schedules():
        sked_dict = filing.get_schedule(sked)
        path_root = "/" + sked
        if sked == 'ReturnHeader990x':
            path_root = "/ReturnHeader"

        if sked == 'IRS990ScheduleK' and type(sked_dict) == listType:
            for individual_sked in sked_dict:
                doc_id = individual_sked.get('@documentId')
                reader = SkedDictReader(
                    _standardizer, _group_dicts, object_id, ein,
                    documentId=doc_id,
                )
                result = reader.parse(individual_sked, parent_path=path_root)
                whole_filing_data.append({
                    'schedule_name': sked,
                    'groups': result['groups'],
                    'schedule_parts': result['schedule_parts'],
                    'csv_line_array': result['csv_line_array'],
                })
                keyerrors.extend(result['keyerrors'])
                group_keyerrors.extend(result['group_keyerrors'])
        else:
            reader = SkedDictReader(
                _standardizer, _group_dicts, object_id, ein,
            )
            result = reader.parse(sked_dict, parent_path=path_root)
            whole_filing_data.append({
                'schedule_name': sked,
                'groups': result['groups'],
                'schedule_parts': result['schedule_parts'],
                'csv_line_array': result['csv_line_array'],
            })
            keyerrors.extend(result['keyerrors'])
            group_keyerrors.extend(result['group_keyerrors'])

    return {
        'file': filename,
        'object_id': object_id,
        'data': whole_filing_data,
        'keyerrors': [ke['element_path'] for ke in keyerrors],
        'group_keyerrors': [gke['element_path'] for gke in group_keyerrors],
        'ok': True,
    }


def _process_one_filing(filepath, output_dir, fmt):
    """Parse a filing and write output to an individual file."""
    result = _parse_filing(filepath)
    if 'error' in result:
        return result

    object_id = result['object_id']
    whole_filing_data = result['data']

    ext = 'json' if fmt == 'json' else 'csv'
    out_path = os.path.join(output_dir, object_id + '.' + ext)

    if fmt == 'json':
        with open(out_path, 'w') as f:
            json.dump(whole_filing_data, f)
    else:
        fieldnames = [
            'schedule_name', 'xpath', 'value', 'db_table', 'db_name',
            'in_group', 'group_name', 'group_index'
        ]
        with open(out_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for sked_result in whole_filing_data:
                for line in sked_result.get('csv_line_array', []):
                    line['schedule_name'] = sked_result['schedule_name']
                    writer.writerow(line)

    return {
        'file': result['file'],
        'ok': True,
        'keyerrors': result['keyerrors'],
        'group_keyerrors': result['group_keyerrors'],
    }


def _output_path_for(object_id, output_dir, fmt):
    """Return the output file path for a given object_id and format."""
    if fmt == 'jsonl':
        return None
    ext = 'json' if fmt == 'json' else 'csv'
    return os.path.join(output_dir, object_id + '.' + ext)


def _print_progress(processed, total, errors, start, workers):
    elapsed = time.time() - start
    rate = processed / elapsed if elapsed > 0 else 0
    print("  [%d/%d] %.0f files/sec | %d errors | %d workers | %.0fs elapsed" % (
        processed, total, rate, errors, workers, elapsed
    ))


def _print_keyerror_report(var_keyerrors, group_keyerrors, output_dir):
    """Print a summary of keyerrors and optionally write to CSV."""
    total_var = sum(var_keyerrors.values())
    total_group = sum(group_keyerrors.values())

    if total_var == 0 and total_group == 0:
        print("\nNo keyerrors found.")
        return

    print("\n--- Keyerror Report ---")

    if total_var > 0:
        print("\nVariable keyerrors (%d total, %d unique xpaths):" % (
            total_var, len(var_keyerrors)
        ))
        for xpath, count in var_keyerrors.most_common(20):
            print("  %5d  %s" % (count, xpath))
        if len(var_keyerrors) > 20:
            print("  ... and %d more unique xpaths" % (len(var_keyerrors) - 20))

    if total_group > 0:
        print("\nGroup keyerrors (%d total, %d unique xpaths):" % (
            total_group, len(group_keyerrors)
        ))
        for xpath, count in group_keyerrors.most_common(20):
            print("  %5d  %s" % (count, xpath))
        if len(group_keyerrors) > 20:
            print("  ... and %d more unique xpaths" % (len(group_keyerrors) - 20))

    # Write full keyerror details to CSV
    keyerrors_path = os.path.join(output_dir, 'keyerrors.csv')
    with open(keyerrors_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['type', 'xpath', 'count'])
        for xpath, count in var_keyerrors.most_common():
            writer.writerow(['variable', xpath, count])
        for xpath, count in group_keyerrors.most_common():
            writer.writerow(['group', xpath, count])
    print("\nFull keyerror report written to %s" % keyerrors_path)


def get_bulk_parser():
    parser = argparse.ArgumentParser("irsx_bulk")
    parser.add_argument(
        'input_dir',
        nargs='?',
        default=None,
        help='Directory containing XML files to parse'
    )
    parser.add_argument(
        '--year',
        default=None,
        help='Process all filings for a 4-digit year. '
             'Looks for <year>*_public.xml in WORKING_DIRECTORY '
             '(override with --input-dir or IRSX_WORKING_DIRECTORY env var).'
    )
    parser.add_argument(
        '--input-dir',
        dest='year_input_dir',
        default=None,
        help='Override input directory when using --year'
    )
    parser.add_argument(
        '--output-dir',
        required=True,
        help='Directory to write parsed output files'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'jsonl'],
        default='json',
        help='Output format (default: json). '
             'jsonl writes all filings to a single .jsonl file.'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of worker processes (default: number of CPUs)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of files to process'
    )
    parser.add_argument(
        '--pattern',
        default='*.xml',
        help='Glob pattern for XML files (default: *.xml)'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        default=False,
        help='Skip files that already have output (json/csv formats only)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=False,
        help='Verbose output'
    )
    return parser


def run_bulk(args):
    # Resolve input directory and pattern
    if args.year:
        input_dir = args.year_input_dir or WORKING_DIRECTORY
        pattern = '%s*_public.xml' % args.year
        print("Processing year %s from %s" % (args.year, input_dir))
    elif args.input_dir:
        input_dir = args.input_dir
        pattern = args.pattern
    else:
        print("Error: provide an input directory or use --year.")
        return

    output_dir = args.output_dir
    fmt = args.format
    workers = args.workers
    verbose = args.verbose
    skip_existing = args.skip_existing
    limit = getattr(args, 'limit', None)

    files = sorted(glob.glob(os.path.join(input_dir, pattern)))
    if not files:
        print("No files matching '%s' found in %s" % (pattern, input_dir))
        return

    os.makedirs(output_dir, exist_ok=True)

    # Filter out already-processed files
    skipped = 0
    if skip_existing and fmt != 'jsonl':
        filtered = []
        for f in files:
            object_id = os.path.basename(f).replace('_public.xml', '')
            out_path = _output_path_for(object_id, output_dir, fmt)
            if os.path.exists(out_path):
                skipped += 1
            else:
                filtered.append(f)
        files = filtered
        if skipped:
            print("Skipping %d already-processed files" % skipped)

    if not files:
        print("All files already processed.")
        return

    # Apply limit
    if limit and limit < len(files):
        print("Limiting to %d of %d files" % (limit, len(files)))
        files = files[:limit]

    actual_workers = workers if workers else (os.cpu_count() or 1)
    total = len(files)
    print("Processing %d files with %d workers..." % (total, actual_workers))

    start = time.time()
    processed = 0
    errors = 0
    var_keyerrors = Counter()
    group_keyerrors = Counter()

    if fmt == 'jsonl':
        jsonl_path = os.path.join(output_dir, 'filings.jsonl')
        with open(jsonl_path, 'w') as jsonl_fh, \
             ProcessPoolExecutor(max_workers=workers, initializer=_init_worker) as executor:

            futures = {
                executor.submit(_parse_filing, f): f
                for f in files
            }

            for future in as_completed(futures):
                result = future.result()
                processed += 1
                if 'error' in result:
                    errors += 1
                    if verbose:
                        print("  Error: %s — %s" % (result['file'], result['error']))
                else:
                    record = {
                        'object_id': result['object_id'],
                        'schedules': result['data'],
                    }
                    jsonl_fh.write(json.dumps(record) + '\n')
                    var_keyerrors.update(result.get('keyerrors', []))
                    group_keyerrors.update(result.get('group_keyerrors', []))

                if processed % 100 == 0:
                    _print_progress(processed, total, errors, start, actual_workers)

    else:
        with ProcessPoolExecutor(
            max_workers=workers,
            initializer=_init_worker
        ) as executor:
            futures = {
                executor.submit(_process_one_filing, f, output_dir, fmt): f
                for f in files
            }

            for future in as_completed(futures):
                result = future.result()
                processed += 1
                if 'error' in result:
                    errors += 1
                    if verbose:
                        print("  Error: %s — %s" % (result['file'], result['error']))
                else:
                    var_keyerrors.update(result.get('keyerrors', []))
                    group_keyerrors.update(result.get('group_keyerrors', []))

                if processed % 100 == 0:
                    _print_progress(processed, total, errors, start, actual_workers)

    _print_progress(processed, total, errors, start, actual_workers)
    print("Output in %s" % output_dir)
    _print_keyerror_report(var_keyerrors, group_keyerrors, output_dir)


def main(args=None):
    parser = get_bulk_parser()
    args = parser.parse_args()
    run_bulk(args)


if __name__ == "__main__":
    main()
