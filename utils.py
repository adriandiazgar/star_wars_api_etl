import logging

import requests

import config


class MemoryCache:
    """
    Memory cache to store key values
    TODO: Expire values based on TTL (time to live)
    """

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.cache = {}

    def set(self, key, value):
        """
        Store a value inside the cache

        :param key: key where the value should be stored
        :param value: value to be stored
        """
        self.cache[key] = value

    def get(self, key, default=None):
        """
        Get a value from the cache
        :param key: key where the value should be present
        :param default: default value to return in case value not present
        :return: value / default value if key not present on cache
        """
        value = self.cache.get(key, default)
        if value and value != default:
            self.log.debug("Cache hit for url: %s", key)
        else:
            self.log.debug("Cache miss for url: %s", key)
        return value


class Requester:
    __cache = MemoryCache()
    log = logging.getLogger("Requester")

    def __get(self, url):
        """
        Function to make a get requests checking first on the cache

        :param url: url
        :return: content stored on the cache or content of the url in case of cache miss
        """
        # First check if thats on the cache (in memory so far)
        if self.__cache.get(url):
            result = self.__cache.get(url)
        else:
            result = requests.get(url).json()
            self.__cache.set(key=url, value=result)
        return result

    def serialize(self, items):
        """
        Serialize items based on attribute _klass
        :param items: list of items to be serialized
        """
        if isinstance(items, list):
            if getattr(self, '_klass', None):
                serialized_items = []
                for item in items:
                    serialized_items.append(self._klass.from_dict(item))
        else:
            serialized_items = self._klass.from_dict(items)
        return serialized_items

    def get_all(self):
        """
        Get all objects of the defined endpoint attribute
        """
        items = []
        url = '{}/{}'.format(config.SWAPI_BASE_URL, self.endpoint)
        self.log.debug("Getting %s", url)
        get_result = self.__get(url)
        items.extend(get_result.get('results', []))
        while get_result.get('next'):
            self.log.debug("Getting %s", get_result.get('next'))
            get_result = self.__get(get_result.get('next'))
            items.extend(get_result.get('results', []))

        return self.serialize(items=items)

    def get_by_url(self, url):
        """
        Get object based on url field
        """
        item = self.__get(url)
        return self.serialize(items=item)
