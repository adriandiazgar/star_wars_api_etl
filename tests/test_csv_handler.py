import os
import tempfile
from unittest import TestCase

from mock import patch, call

from csv_handler import CSVHandler


class TestFileContent:
    def __init__(self, content):
        self.file = tempfile.NamedTemporaryFile(mode='w', delete=False)

        with self.file as f:
            f.write(content)

    @property
    def filename(self):
        return self.file.name

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        os.unlink(self.filename)


class TestCSVHandler(TestCase):

    def test_no_fields_provided(self):
        with self.assertRaises(CSVHandler.MissingCSVFields):
            CSVHandler(items=[])

    @patch('csv_handler.csv')
    def test_write_csv_file(self, mock_csv):
        class DummyStructure:
            def __init__(self, text1, value1, text2):
                self.text1 = text1
                self.text2 = text2
                self.value1 = value1

        tmp_file = TestFileContent(content='')
        csv = CSVHandler(items=[DummyStructure('text1', 2, 'text2')],
                         fields={'header_text1': 'text1', 'header_value1': 'value1', 'header_text2': 'text2'},
                         file_path=tmp_file.filename)

        mock_csv.writer.assert_called_once()
        calls = [call().writerow({'header_text1': '', 'header_value1': '', 'header_text2': ''}.keys()),
                 call().writerow(['text1', '2', 'text2'])]
        mock_csv.writer.assert_has_calls(calls)
        self.assertEqual(mock_csv.writer.call_args.args[0].name, tmp_file.filename)
        self.assertEqual(mock_csv.writer.call_args.kwargs['delimiter'], ',')
        self.assertEqual(mock_csv.writer.call_args.kwargs['quotechar'], '"')
        self.assertEqual(mock_csv.writer.call_args.kwargs['quoting'], mock_csv.QUOTE_MINIMAL)
