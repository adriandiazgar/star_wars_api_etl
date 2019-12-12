import json
from unittest import TestCase

import requests_mock

from utils import MemoryCache, Requester


class TestMemoryCache(TestCase):
    def test_set_and_get_value(self):
        cache = MemoryCache()
        cache.set(key='testkey', value='testvalue')
        read_value = cache.get(key='testkey')
        self.assertEqual(read_value, 'testvalue')
        read_default_value = cache.get(key='invalid_key', default='default_value')
        self.assertEqual(read_default_value, 'default_value')
        read_default_value = cache.get(key='invalid_key')
        self.assertIsNone(read_default_value)


class TestRequester(TestCase):

    @requests_mock.mock()
    def test_private_get_cache_miss(self, request_mock):
        request_mock.get('http://fake_url', text=json.dumps({'data_request': 'value_request'}))
        requester = Requester()
        result = requester._Requester__get('http://fake_url')
        self.assertEqual(result, {'data_request': 'value_request'})

    def test_private_get_cache_hit(self):
        requester = Requester()
        requester._Requester__cache.set(key='http://fake_url2', value='cache_data')
        result = requester._Requester__get('http://fake_url2')
        self.assertEqual(result, 'cache_data')
