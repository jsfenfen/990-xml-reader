"""
Tests for the irsx library.

Uses test XML files copied from 990-xml-reader-rust/test_data/.
"""
import os
import json
import time
import pytest

from irs_reader.standardizer import Standardizer, Documentizer, VersionDocumentizer
from irs_reader.type_utils import (
    dictType, orderedDictType, listType, unicodeType, noneType, strType
)
from irs_reader.filing import Filing, InvalidXMLException, FileMissingException
from irs_reader.xmlrunner import XMLRunner
from irs_reader.file_utils import validate_object_id
from irs_reader.settings import (
    METADATA_DIRECTORY, KNOWN_SCHEDULES, version_is_supported
)
from irs_reader.irsx_cli import get_parser, run_main
from irs_reader.irsx_retrieve_cli import (
    discover_zip_urls, get_cli_retrieve_parser
)
from irs_reader.irsx_bulk_cli import get_bulk_parser, run_bulk

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

# Sutter Health Sacramento Region 2014 filing — has multiple schedule K's
FILING_2014V50_ID = '201533089349301428'
FILING_2014V50_PATH = os.path.join(TEST_DATA_DIR, '201533089349301428_public.xml')

# 990EZ filing
FILING_2016_ID = '201600089349200000'
FILING_2016_PATH = os.path.join(TEST_DATA_DIR, '201600089349200000_public.xml')

# All test files with expected versions (mirrors Rust integration_test.rs)
ALL_SUPPORTED_FILES = [
    ('201401349349302815_public.xml', '2013v3.0'),
    ('201500429349300330_public.xml', '2013v4.0'),
    ('201500089349200000_public.xml', '2014v5.0'),
    ('201600619349300750_public.xml', '2014v6.0'),
    ('201601249349100900_public.xml', '2015v2.0'),
    ('201600089349200000_public.xml', '2015v2.1'),
    ('201700119349300100_public.xml', '2015v3.0'),
    ('201800099349200510_public.xml', '2016v3.0'),
    ('201900099349300620_public.xml', '2017v2.3'),
    ('202000089349300010_public.xml', '2018v3.1'),
    ('202100089349301760_public.xml', '2019v5.0'),
    ('202200079349301550_public.xml', '2020v4.1'),
    ('202202589349301980_public.xml', '2021v4.2'),
    ('202403589349300950_public.xml', '2023v5.1'),
    ('202600219349300420_public.xml', '2024v5.2'),
]

UNSUPPORTED_FILE = '200931393493000150_public.xml'


def _parse_test_filing(filename):
    """Parse a test filing and return (Filing, XMLRunner) with results."""
    object_id = filename.replace('_public.xml', '')
    filepath = os.path.join(TEST_DATA_DIR, filename)
    f = Filing(object_id, filepath=filepath)
    f.process()

    runner = XMLRunner()
    if version_is_supported(f.get_version()):
        ein = f.get_ein()
        for sked in f.list_schedules():
            sked_dict = f.get_schedule(sked)
            runner._run_schedule(sked, object_id, sked_dict, ein)
    return f, runner


# ── Metadata loading tests ──────────────────────────────────────────────


class TestMetadataFiles:
    """Verify that the metadata CSV files exist and are loadable."""

    def test_metadata_directory_exists(self):
        assert os.path.isdir(METADATA_DIRECTORY)

    def test_metadata_csv_files_exist(self):
        for fname in ['variables.csv', 'groups.csv', 'schedule_parts.csv',
                       'line_numbers.csv', 'descriptions.csv']:
            path = os.path.join(METADATA_DIRECTORY, fname)
            assert os.path.isfile(path), f"Missing metadata file: {fname}"


class TestStandardizer:

    def test_loads_variables(self):
        s = Standardizer()
        assert len(s.variables) > 100

    def test_loads_groups(self):
        s = Standardizer()
        assert len(s.groups) > 10

    def test_get_var(self):
        s = Standardizer()
        var = s.get_var('/IRS990/TotalAssetsEOYAmt')
        assert 'db_table' in var
        assert 'db_name' in var

    def test_get_var_missing_raises(self):
        s = Standardizer()
        with pytest.raises(KeyError):
            s.get_var('/IRS990/TotallyBogusField')


class TestDocumentizer:

    def test_loads_with_extra_columns(self):
        d = Documentizer()
        assert len(d.variables) > 100
        # Documentizer loads more columns per variable
        sample_var = next(iter(d.variables.values()))
        assert 'db_type' in sample_var
        assert 'description' in sample_var

    def test_loads_schedule_parts(self):
        d = Documentizer()
        assert len(d.schedule_parts) > 10

    def test_get_parts_by_sked(self):
        d = Documentizer()
        parts = d.get_parts_by_sked('IRS990')
        assert len(parts) > 0

    def test_get_groups_by_sked(self):
        d = Documentizer()
        groups = d.get_groups_by_sked('IRS990')
        assert len(groups) > 0

    def test_with_versions(self):
        d = Documentizer(versions=True)
        sample_var = next(iter(d.variables.values()))
        assert 'version_start' in sample_var


class TestVersionDocumentizer:

    def test_loads_line_numbers(self):
        vd = VersionDocumentizer()
        assert len(vd.line_numbers) > 100

    def test_loads_descriptions(self):
        vd = VersionDocumentizer()
        assert len(vd.descriptions) > 100

    def test_get_line_number(self):
        vd = VersionDocumentizer()
        result = vd.get_line_number('/IRS990/TotalAssetsEOYAmt', '2016v3.0')
        assert result is not None

    def test_get_description(self):
        vd = VersionDocumentizer()
        result = vd.get_description('/IRS990/TotalAssetsEOYAmt', '2016v3.0')
        assert result is not None

    def test_missing_xpath_returns_none(self):
        vd = VersionDocumentizer()
        assert vd.get_line_number('/BogusPath', '2016v3.0') is None
        assert vd.get_description('/BogusPath', '2016v3.0') is None


# ── Type utils tests ────────────────────────────────────────────────────


class TestTypeUtils:

    def test_dict_type(self):
        assert type({}) == dictType

    def test_ordered_dict_type(self):
        from collections import OrderedDict
        assert type(OrderedDict()) == orderedDictType

    def test_list_type(self):
        assert type([]) == listType

    def test_unicode_type(self):
        assert unicodeType is str

    def test_none_type(self):
        assert type(None) == noneType

    def test_str_type(self):
        assert strType is str


# ── Filing tests ────────────────────────────────────────────────────────


class TestFiling:

    def test_process_with_filepath(self):
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        assert f.get_version() == '2014v5.0'

    def test_ein(self):
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        assert f.get_ein() == '941156621'

    def test_schedules_listed(self):
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        skeds = f.list_schedules()
        assert 'ReturnHeader990x' in skeds
        assert 'IRS990' in skeds

    def test_get_type_990(self):
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        assert f.get_type() == 'IRS990'

    def test_get_schedule(self):
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        header = f.get_schedule('ReturnHeader990x')
        assert header is not None

    def test_get_unparsed_json(self):
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        raw = f.get_unparsed_json()
        parsed = json.loads(raw)
        assert 'Return' in parsed

    def test_filing_missing_raises(self):
        with pytest.raises(FileMissingException):
            f = Filing('201400000000000000', filepath='/nonexistent/path.xml')
            f.process()

    def test_990ez_filing(self):
        f = Filing(FILING_2016_ID, filepath=FILING_2016_PATH)
        f.process()
        assert f.get_type() == 'IRS990EZ'


# ── XMLRunner tests ─────────────────────────────────────────────────────


class TestXMLRunner:

    def test_run_filing_with_filepath(self):
        """Test the full parse pipeline using a Filing with explicit path."""
        standardizer = Standardizer()
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        assert version_is_supported(f.get_version())

        runner = XMLRunner()
        ein = f.get_ein()
        for sked in f.list_schedules():
            sked_dict = f.get_schedule(sked)
            runner._run_schedule(sked, FILING_2014V50_ID, sked_dict, ein)

        assert len(runner.whole_filing_data) > 0

    def test_parses_all_schedules(self):
        """Test that all schedules in the filing are parsed."""
        runner = XMLRunner()
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        skeds = f.list_schedules()
        assert 'IRS990ScheduleJ' in skeds

        ein = f.get_ein()
        for sked in skeds:
            sked_dict = f.get_schedule(sked)
            runner._run_schedule(sked, FILING_2014V50_ID, sked_dict, ein)

        parsed_sked_names = [r['schedule_name'] for r in runner.whole_filing_data]
        for sked in skeds:
            assert sked in parsed_sked_names

    def test_documentation_mode(self):
        runner = XMLRunner(documentation=True)
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        ein = f.get_ein()
        sked_dict = f.get_schedule('IRS990')
        runner._run_schedule('IRS990', FILING_2014V50_ID, sked_dict, ein)
        result = runner.whole_filing_data[0]
        # In documentation mode, schedule_parts values are dicts with metadata
        for table_name, table_data in result['schedule_parts'].items():
            for key, val in table_data.items():
                if key not in ('object_id', 'ein', 'documentId'):
                    assert isinstance(val, dict), f"Expected dict for {key}"
                    assert 'value' in val
                    break
            break

    def test_csv_format_mode(self):
        runner = XMLRunner(csv_format=True)
        f = Filing(FILING_2014V50_ID, filepath=FILING_2014V50_PATH)
        f.process()
        ein = f.get_ein()
        sked_dict = f.get_schedule('IRS990')
        runner._run_schedule('IRS990', FILING_2014V50_ID, sked_dict, ein)
        result = runner.whole_filing_data[0]
        assert len(result['csv_line_array']) > 0


# ── Validation tests ────────────────────────────────────────────────────


class TestValidation:

    def test_valid_object_id(self):
        result = validate_object_id('201533089349301428')
        assert result == '201533089349301428'

    def test_invalid_object_id_raises(self):
        with pytest.raises(RuntimeError):
            validate_object_id('12345')


# ── Settings / version string tests ─────────────────────────────────────


class TestSettings:

    def test_version_is_supported(self):
        assert version_is_supported('2013v3.0')
        assert version_is_supported('2016v3.1')
        assert version_is_supported('2024v7.0')
        assert version_is_supported('2030v1.0')

    def test_version_not_supported(self):
        assert not version_is_supported('2012v3.0')
        assert not version_is_supported('2010v3.2')
        assert not version_is_supported('garbage')

    def test_known_schedules(self):
        assert 'IRS990' in KNOWN_SCHEDULES
        assert 'IRS990EZ' in KNOWN_SCHEDULES
        assert 'IRS990PF' in KNOWN_SCHEDULES
        assert 'ReturnHeader990x' in KNOWN_SCHEDULES


# ── Cross-version filing tests ─────────────────────────────────────────


class TestVersionSupport:
    """Test version detection across all schema versions (2013v3.0–2024v5.2)."""

    def test_unsupported_version(self):
        filepath = os.path.join(TEST_DATA_DIR, UNSUPPORTED_FILE)
        f = Filing('200931393493000150', filepath=filepath)
        f.process()
        assert f.get_version() == '2008v2.7'
        assert not version_is_supported(f.get_version())

    @pytest.mark.parametrize('filename,expected_version', ALL_SUPPORTED_FILES)
    def test_supported_version(self, filename, expected_version):
        filepath = os.path.join(TEST_DATA_DIR, filename)
        object_id = filename.replace('_public.xml', '')
        f = Filing(object_id, filepath=filepath)
        f.process()
        assert f.get_version() == expected_version
        assert version_is_supported(f.get_version())


class TestEINExtraction:
    """Test EIN extraction across versions."""

    @pytest.mark.parametrize('filename,expected_ein', [
        ('201401349349302815_public.xml', '200400774'),
        ('201401439349100200_public.xml', '141833603'),
        ('201500089349200000_public.xml', '453658221'),
        ('201601249349100900_public.xml', '046662754'),
        ('202100089349301760_public.xml', '271822009'),
        ('202600219349300420_public.xml', '060996545'),
    ])
    def test_ein(self, filename, expected_ein):
        filepath = os.path.join(TEST_DATA_DIR, filename)
        object_id = filename.replace('_public.xml', '')
        f = Filing(object_id, filepath=filepath)
        f.process()
        assert f.get_ein() == expected_ein


class TestFormTypeDetection:
    """Test 990 vs 990EZ vs 990PF detection."""

    @pytest.mark.parametrize('filename', [
        '201403019349300800_public.xml',
        '201900099349300620_public.xml',
        '202403589349300950_public.xml',
    ])
    def test_990_detection(self, filename):
        filepath = os.path.join(TEST_DATA_DIR, filename)
        object_id = filename.replace('_public.xml', '')
        f = Filing(object_id, filepath=filepath)
        f.process()
        assert f.get_type() == 'IRS990'

    @pytest.mark.parametrize('filename', [
        '201500089349200000_public.xml',
        '201800099349200510_public.xml',
        '202300129349200500_public.xml',
    ])
    def test_990ez_detection(self, filename):
        filepath = os.path.join(TEST_DATA_DIR, filename)
        object_id = filename.replace('_public.xml', '')
        f = Filing(object_id, filepath=filepath)
        f.process()
        assert f.get_type() == 'IRS990EZ'

    def test_990pf_detection(self):
        filepath = os.path.join(TEST_DATA_DIR, '201401439349100200_public.xml')
        f = Filing('201401439349100200', filepath=filepath)
        f.process()
        assert f.get_type() == 'IRS990PF'


class TestScheduleDetection:
    """Test schedule listing across form types and years."""

    def test_990_with_many_schedules(self):
        f, _ = _parse_test_filing('201403019349300800_public.xml')
        skeds = f.list_schedules()
        assert len(skeds) == 10
        assert 'IRS990ScheduleA' in skeds
        assert 'IRS990ScheduleJ' in skeds
        assert 'IRS990ScheduleR' in skeds

    def test_2025_filing_schedules(self):
        f, _ = _parse_test_filing('202403589349300950_public.xml')
        skeds = f.list_schedules()
        assert len(skeds) >= 8
        assert 'ReturnHeader990x' in skeds
        assert 'IRS990' in skeds

    def test_990pf_minimal_schedules(self):
        f, _ = _parse_test_filing('201601249349100900_public.xml')
        skeds = f.list_schedules()
        assert len(skeds) == 2
        assert 'ReturnHeader990x' in skeds
        assert 'IRS990PF' in skeds


class TestFieldExtraction:
    """Test standardized field extraction across versions."""

    def test_return_header_fields(self):
        _, runner = _parse_test_filing('201401349349302815_public.xml')
        header = [r for r in runner.whole_filing_data
                  if r['schedule_name'] == 'ReturnHeader990x'][0]
        assert 'returnheader990x_part_i' in header['schedule_parts']
        part = header['schedule_parts']['returnheader990x_part_i']
        assert part['Flr_EIN'] == '200400774'

    def test_990_key_fields_2014(self):
        _, runner = _parse_test_filing('201533089349301428_public.xml')
        irs990 = [r for r in runner.whole_filing_data
                  if r['schedule_name'] == 'IRS990'][0]
        assert 'part_0' in irs990['schedule_parts']
        part_0 = irs990['schedule_parts']['part_0']
        assert part_0['PrncplOffcrNm'] == 'JAMES CONFORTI'
        assert part_0['GrssRcptsAmt'] == '4246318454'

    def test_990_has_schedule_parts_2025(self):
        _, runner = _parse_test_filing('202403589349300950_public.xml')
        irs990 = [r for r in runner.whole_filing_data
                  if r['schedule_name'] == 'IRS990'][0]
        assert len(irs990['schedule_parts']) > 0

    @pytest.mark.parametrize('filename', [
        '201403019349300800_public.xml',
        '202100089349301760_public.xml',
    ])
    def test_990_repeating_groups(self, filename):
        _, runner = _parse_test_filing(filename)
        irs990 = [r for r in runner.whole_filing_data
                  if r['schedule_name'] == 'IRS990'][0]
        assert len(irs990['groups']) > 0


class TestAllFilesParse:
    """Verify every test file parses without error."""

    def test_all_supported_files_parse(self):
        failures = []
        for filename, _ in ALL_SUPPORTED_FILES:
            try:
                f, runner = _parse_test_filing(filename)
                assert len(runner.whole_filing_data) > 0, \
                    "No parsed data for %s" % filename
            except Exception as e:
                failures.append('%s: %s' % (filename, e))

        assert not failures, \
            "%d/%d files failed:\n  %s" % (
                len(failures), len(ALL_SUPPORTED_FILES),
                '\n  '.join(failures)
            )

    def test_all_supported_files_have_schedules(self):
        for filename, version in ALL_SUPPORTED_FILES:
            f, runner = _parse_test_filing(filename)
            sked_names = [r['schedule_name'] for r in runner.whole_filing_data]
            assert len(sked_names) >= 2, \
                "Expected at least 2 schedules for %s (%s), got %d" % (
                    filename, version, len(sked_names)
                )


# ── Bulk processing tests ────────────────────────────────────────────────


class TestBulk:

    def test_bulk_json(self, tmp_path):
        output_dir = str(tmp_path / 'json_out')
        parser = get_bulk_parser()
        args = parser.parse_args([
            TEST_DATA_DIR, '--output-dir', output_dir, '--format', 'json'
        ])
        run_bulk(args)

        out_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        assert len(out_files) == 21  # 22 test files minus 1 unsupported

        # Verify output is valid JSON with schedule data
        for f in out_files:
            with open(os.path.join(output_dir, f)) as fh:
                data = json.load(fh)
            assert isinstance(data, list)
            assert len(data) > 0
            assert 'schedule_name' in data[0]

    def test_bulk_csv(self, tmp_path):
        output_dir = str(tmp_path / 'csv_out')
        parser = get_bulk_parser()
        args = parser.parse_args([
            TEST_DATA_DIR, '--output-dir', output_dir, '--format', 'csv'
        ])
        run_bulk(args)

        csv_files = [f for f in os.listdir(output_dir) if f != 'keyerrors.csv']
        assert len(csv_files) == 21  # 22 test files minus 1 unsupported
        for f in csv_files:
            assert os.path.getsize(os.path.join(output_dir, f)) > 0

    def test_bulk_with_workers(self, tmp_path):
        output_dir = str(tmp_path / 'workers_out')
        parser = get_bulk_parser()
        args = parser.parse_args([
            TEST_DATA_DIR, '--output-dir', output_dir, '--workers', '2'
        ])
        run_bulk(args)
        json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        assert len(json_files) == 21  # 22 test files minus 1 unsupported

    def test_bulk_parser(self):
        parser = get_bulk_parser()
        args = parser.parse_args([
            '/some/dir', '--output-dir', '/out', '--format', 'csv',
            '--workers', '4', '--pattern', '*.xml', '--verbose',
            '--skip-existing'
        ])
        assert args.input_dir == '/some/dir'
        assert args.output_dir == '/out'
        assert args.format == 'csv'
        assert args.workers == 4
        assert args.pattern == '*.xml'
        assert args.verbose is True
        assert args.skip_existing is True

    def test_bulk_parser_year(self):
        parser = get_bulk_parser()
        args = parser.parse_args([
            '--year', '2024', '--output-dir', '/out'
        ])
        assert args.year == '2024'
        assert args.output_dir == '/out'
        assert args.input_dir is None

    def test_bulk_year_mode(self, tmp_path):
        """--year filters to files starting with that year prefix."""
        # Create a fake input dir with files from different years
        input_dir = str(tmp_path / 'xml')
        os.makedirs(input_dir)
        import shutil
        shutil.copy(FILING_2014V50_PATH, input_dir)  # 2015...
        shutil.copy(FILING_2016_PATH, input_dir)      # 2016...

        output_dir = str(tmp_path / 'out')
        parser = get_bulk_parser()
        # Only process 2016 filings
        args = parser.parse_args([
            '--year', '2016', '--input-dir', input_dir,
            '--output-dir', output_dir
        ])
        run_bulk(args)

        out_files = os.listdir(output_dir)
        assert len(out_files) == 1
        assert out_files[0].startswith('2016')

    def test_bulk_empty_dir(self, tmp_path, capsys):
        empty_dir = str(tmp_path / 'empty')
        os.makedirs(empty_dir)
        output_dir = str(tmp_path / 'out')
        parser = get_bulk_parser()
        args = parser.parse_args([empty_dir, '--output-dir', output_dir])
        run_bulk(args)
        captured = capsys.readouterr()
        assert 'No files' in captured.out

    def test_bulk_jsonl(self, tmp_path):
        output_dir = str(tmp_path / 'jsonl_out')
        parser = get_bulk_parser()
        args = parser.parse_args([
            TEST_DATA_DIR, '--output-dir', output_dir, '--format', 'jsonl'
        ])
        run_bulk(args)

        jsonl_path = os.path.join(output_dir, 'filings.jsonl')
        assert os.path.isfile(jsonl_path)

        lines = open(jsonl_path).readlines()
        assert len(lines) == 21  # 22 test files minus 1 unsupported

        for line in lines:
            record = json.loads(line)
            assert 'object_id' in record
            assert 'schedules' in record
            assert isinstance(record['schedules'], list)
            assert len(record['schedules']) > 0

    def test_bulk_skip_existing(self, tmp_path):
        output_dir = str(tmp_path / 'skip_out')
        parser = get_bulk_parser()

        # First run: process all files
        args = parser.parse_args([
            TEST_DATA_DIR, '--output-dir', output_dir, '--format', 'json'
        ])
        run_bulk(args)
        json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        assert len(json_files) == 21  # 22 test files minus 1 unsupported

        # Record mtimes of json files only
        mtimes = {}
        for f in json_files:
            mtimes[f] = os.path.getmtime(os.path.join(output_dir, f))

        # Small delay so mtime would change if file were rewritten
        time.sleep(0.05)

        # Second run with --skip-existing: should not reprocess
        args = parser.parse_args([
            TEST_DATA_DIR, '--output-dir', output_dir, '--format', 'json',
            '--skip-existing'
        ])
        run_bulk(args)

        # JSON files should be untouched
        for f in json_files:
            assert os.path.getmtime(os.path.join(output_dir, f)) == mtimes[f]

    def test_bulk_skip_existing_partial(self, tmp_path):
        """If one output exists and one doesn't, only process the missing one."""
        output_dir = str(tmp_path / 'partial_out')
        os.makedirs(output_dir)
        parser = get_bulk_parser()

        # Pre-create one output file
        with open(os.path.join(output_dir, FILING_2014V50_ID + '.json'), 'w') as f:
            f.write('[]')

        args = parser.parse_args([
            TEST_DATA_DIR, '--output-dir', output_dir, '--format', 'json',
            '--skip-existing'
        ])
        run_bulk(args)

        # All should exist now (21 supported + keyerrors.csv potentially)
        json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        assert len(json_files) == 21  # 22 test files minus 1 unsupported
        # The pre-existing one should still be our dummy
        with open(os.path.join(output_dir, FILING_2014V50_ID + '.json')) as f:
            assert f.read() == '[]'
        # Another should be real parsed data
        with open(os.path.join(output_dir, FILING_2016_ID + '.json')) as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0


    def test_bulk_keyerror_report(self, tmp_path):
        output_dir = str(tmp_path / 'ke_out')
        parser = get_bulk_parser()
        args = parser.parse_args([
            TEST_DATA_DIR, '--output-dir', output_dir
        ])
        run_bulk(args)

        keyerrors_path = os.path.join(output_dir, 'keyerrors.csv')
        assert os.path.isfile(keyerrors_path)

        import csv as csv_mod
        with open(keyerrors_path) as f:
            reader = csv_mod.DictReader(f)
            rows = list(reader)
        assert len(rows) > 0
        assert rows[0]['type'] in ('variable', 'group')
        assert int(rows[0]['count']) > 0

    def test_bulk_limit(self, tmp_path):
        output_dir = str(tmp_path / 'limit_out')
        parser = get_bulk_parser()
        args = parser.parse_args([
            TEST_DATA_DIR, '--output-dir', output_dir, '--limit', '3'
        ])
        run_bulk(args)

        json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        # 3 files processed; first is unsupported (2008), so 2 outputs
        assert len(json_files) == 2


# ── Retrieve / download tests ────────────────────────────────────────────


class TestRetrieve:

    def test_discover_zip_urls_2024(self):
        urls = discover_zip_urls('2024')
        assert len(urls) > 0
        assert all(u.endswith('.zip') for u in urls)
        assert all('/2024/' in u for u in urls)

    def test_discover_zip_urls_old_year_empty(self):
        urls = discover_zip_urls('2010')
        assert len(urls) == 0

    def test_retrieve_parser_irs(self):
        parser = get_cli_retrieve_parser()
        args = parser.parse_args(['irs', '2024', '--verbose'])
        assert args.source == 'irs'
        assert args.year == ['2024']
        assert args.verbose is True

    def test_retrieve_parser_irs_multiple_years(self):
        parser = get_cli_retrieve_parser()
        args = parser.parse_args(['irs', '2023', '2024'])
        assert args.year == ['2023', '2024']

    def test_retrieve_parser_irs_index_only(self):
        parser = get_cli_retrieve_parser()
        args = parser.parse_args(['irs', '2024', '--index-only'])
        assert args.index_only is True

    def test_retrieve_parser_irs_output_dir(self):
        parser = get_cli_retrieve_parser()
        args = parser.parse_args(['irs', '2024', '--output-dir', '/tmp/xml'])
        assert args.output_dir == '/tmp/xml'

    def test_retrieve_parser_archive(self):
        parser = get_cli_retrieve_parser()
        args = parser.parse_args(['archive', '2015', '2016'])
        assert args.source == 'archive'
        assert args.year == ['2015', '2016']

    def test_retrieve_parser_archive_output_dir(self):
        parser = get_cli_retrieve_parser()
        args = parser.parse_args(['archive', '2015', '--output-dir', '/tmp/xml'])
        assert args.output_dir == '/tmp/xml'


# ── CLI parser tests ────────────────────────────────────────────────────


class TestCLIParser:

    def test_parser_basic(self):
        parser = get_parser()
        args = parser.parse_args(['201533089349301428'])
        assert args.object_ids == [201533089349301428]
        assert args.format == 'json'
        assert args.verbose is False

    def test_parser_verbose(self):
        parser = get_parser()
        args = parser.parse_args(['201533089349301428', '--verbose'])
        assert args.verbose is True

    def test_parser_schedule(self):
        parser = get_parser()
        args = parser.parse_args(['--schedule', 'IRS990', '201533089349301428'])
        assert args.schedule == 'IRS990'

    def test_parser_format_csv(self):
        parser = get_parser()
        args = parser.parse_args(['--format', 'csv', '201533089349301428'])
        assert args.format == 'csv'

    def test_parser_format_txt(self):
        parser = get_parser()
        args = parser.parse_args(['--format', 'txt', '201533089349301428'])
        assert args.format == 'txt'

    def test_parser_file_output(self):
        parser = get_parser()
        args = parser.parse_args(['--file', 'out.json', '201533089349301428'])
        assert args.file == 'out.json'

    def test_parser_list_schedules(self):
        parser = get_parser()
        args = parser.parse_args(['--list_schedules', '201533089349301428'])
        assert args.list_schedules is True


# ── CLI execution tests (with file output to avoid stdout issues) ───────


class TestCLIExecution:

    def test_json_output_to_file(self, tmp_path):
        outfile = str(tmp_path / 'out.json')
        parser = get_parser()
        args = parser.parse_args([
            '--file', outfile, FILING_2014V50_ID
        ])
        # Need file in working directory — use Filing with filepath instead
        # We'll test CLI parser + run_main with file output
        # First, symlink or copy the test file to where Filing expects it
        from irs_reader.settings import WORKING_DIRECTORY
        expected_path = os.path.join(WORKING_DIRECTORY, f'{FILING_2014V50_ID}_public.xml')
        os.makedirs(WORKING_DIRECTORY, exist_ok=True)
        if not os.path.exists(expected_path):
            os.symlink(FILING_2014V50_PATH, expected_path)
        try:
            run_main(args)
            assert os.path.isfile(outfile)
            with open(outfile) as f:
                data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0
        finally:
            if os.path.islink(expected_path):
                os.unlink(expected_path)

    def test_csv_output_to_file(self, tmp_path):
        outfile = str(tmp_path / 'out.csv')
        parser = get_parser()
        args = parser.parse_args([
            '--format', 'csv', '--file', outfile, FILING_2014V50_ID
        ])
        from irs_reader.settings import WORKING_DIRECTORY
        expected_path = os.path.join(WORKING_DIRECTORY, f'{FILING_2014V50_ID}_public.xml')
        os.makedirs(WORKING_DIRECTORY, exist_ok=True)
        if not os.path.exists(expected_path):
            os.symlink(FILING_2014V50_PATH, expected_path)
        try:
            run_main(args)
            assert os.path.isfile(outfile)
            assert os.path.getsize(outfile) > 0
        finally:
            if os.path.islink(expected_path):
                os.unlink(expected_path)

    def test_txt_output_to_file(self, tmp_path):
        outfile = str(tmp_path / 'out.txt')
        parser = get_parser()
        args = parser.parse_args([
            '--format', 'txt', '--file', outfile, FILING_2014V50_ID
        ])
        from irs_reader.settings import WORKING_DIRECTORY
        expected_path = os.path.join(WORKING_DIRECTORY, f'{FILING_2014V50_ID}_public.xml')
        os.makedirs(WORKING_DIRECTORY, exist_ok=True)
        if not os.path.exists(expected_path):
            os.symlink(FILING_2014V50_PATH, expected_path)
        try:
            run_main(args)
            assert os.path.isfile(outfile)
            assert os.path.getsize(outfile) > 0
        finally:
            if os.path.islink(expected_path):
                os.unlink(expected_path)
