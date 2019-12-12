import json
import os
import tempfile
from unittest import TestCase

import requests_mock
from requests.exceptions import HTTPError

import config
from httpbin import HTTPBin


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


class TestHTTPBin(TestCase):
    @requests_mock.mock()
    def test_send_file_status_different_than_200(self, request_mock):
        httpbin_client = HTTPBin()
        request_mock.post("{}/{}".format(config.HTTPBIN_BASE_URL, config.HTTPBIN_FILE_ENDPOINT), text='error',
                          status_code=401)
        tmp_file = TestFileContent(content='test_data')
        with self.assertRaises(HTTPError):
            httpbin_client.send_file(file=tmp_file.filename)

    @requests_mock.mock()
    def test_send_file_status_200_fail_integrity_check(self, request_mock):
        httpbin_client = HTTPBin()
        request_mock.post("{}/{}".format(config.HTTPBIN_BASE_URL, config.HTTPBIN_FILE_ENDPOINT),
                          text=json.dumps({'files': {'file': 'test_data_wrong'}}))
        tmp_file = TestFileContent(content='test_data')
        with self.assertRaises(HTTPBin.FileIntegrityError):
            httpbin_client.send_file(file=tmp_file.filename)

    @requests_mock.mock()
    def test_send_file_status_200_integrity_check_ok(self, request_mock):
        httpbin_client = HTTPBin()
        request_mock.post("{}/{}".format(config.HTTPBIN_BASE_URL, config.HTTPBIN_FILE_ENDPOINT),
                          text=json.dumps({'files': {'file': 'test_data'}}))
        tmp_file = TestFileContent(content='test_data')
        httpbin_client.send_file(file=tmp_file.filename)
