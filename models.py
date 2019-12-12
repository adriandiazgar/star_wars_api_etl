import config
from utils import Requester


class BaseQuerySet(Requester):
    """
    Base query set to implement specific query sets
    """

    def __init__(self, items=None, foreign_keys=None):
        """
        :param items: items to initialize inside the query set
        :param foreign_keys: foreign keys inside the query set (fields that depends on other query sets)
        """
        super(BaseQuerySet, self).__init__()
        if not items:
            items = []

        if not foreign_keys:
            foreign_keys = []

        self.items = items
        self.foreign_keys = foreign_keys

    def get_all(self):
        """
        Get all objects and add them to self.items
        :return: itself
        """
        self.items = super(BaseQuerySet, self).get_all()
        return self

    def get_by_url(self, url):
        """
        Get object by url, useful when resolving foreign_keys
        :param url: url to fetch the object from
        :return: itself
        """
        self.items = [super(BaseQuerySet, self).get_by_url(url)]
        return self

    def order_by(self, attribute, desc=True):
        """
        Order items by attribute
        :param attribute: attribute to sort by
        :param desc: Descending (True) / Ascending (False)
        :return: a query set with ordered items sorted by the attribute
        """
        sorted_list = []
        for f in sorted(self.items, key=lambda i: getattr(i, attribute) if getattr(i, attribute) else -1,
                        reverse=desc):
            sorted_list.append(f)
        return self.__class__(items=sorted_list, foreign_keys=self.foreign_keys)

    def resolve_foreign_keys(self):
        """
        Resolve foreign keys requesting the object inside the URL contain in the field
        For example
        Person:
        - name: John
        - species: https://myurlspecie/1
        - otherfield: value

        species should be defined on self.foreign_keys when calling this function and they will get resolved.
        :return: it will replace the urls by the actual 'name field of the foreign object'
        """
        self.resolve_foreign_keys = True
        for field, query_set_class in self.foreign_keys.items():
            for item in self.items:
                url = getattr(item, field)
                result = query_set_class.get_by_url(url=url)
                setattr(item, field, result.name)  # Assuming that every single model has name

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self.items))
            return self.__class__(items=[self.items[i] for i in range(start, stop, step)],
                                  foreign_keys=self.foreign_keys)
        elif isinstance(key, int):
            return self.items[key]
        elif isinstance(key, tuple):
            raise NotImplementedError('Tuple as index')
        else:
            raise TypeError('Invalid argument type: {}'.format(type(key)))

    def __iter__(self):
        for item in self.items:
            yield item

    def __len__(self):
        return len(self.items)


class Person:
    @classmethod
    def from_dict(cls, dict):
        """
        Factory method to generate an object based on its dictionary
        :param dict: dictionary with the fields
        :return: Person object
        """
        return cls(name=dict.get('name'), height=dict.get('height'), films=dict.get('films'),
                   species=dict.get('species'))

    def __init__(self, name, height, films, species):
        """

        :param name: Person name
        :param height: Person height (string / integer)
        :param films: List of films where the person appears
        :param species: Person species list
        """
        self.name = name
        self.height = int(height) if height.isdigit() else None
        self.species = species.pop() if species else None
        self.films_count = len(films)

    def __unicode__(self):
        return u'<Person - {}>'.format(self.name)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()


class Species:
    @classmethod
    def from_dict(cls, dict):
        """
        Factory method to generate an object based on its dictionary
        :param dict: dictionary with the fields
        :return: Species object
        """

        return cls(name=dict.get('name'))

    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return u'<Species - {}>'.format(self.name)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()


class SpeciesQuerySet(BaseQuerySet):
    """
    Species queryset defining the endpoint and the class to serialize the species object
    """
    endpoint = config.SPECIES
    _klass = Species

    @property
    def name(self):
        """
        Species name property
        """
        return self.items.pop().name

    def __unicode__(self):
        return u'<SpeciesQuerySet - {}>'.format(len(self))

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()


class PeopleQuerySet(BaseQuerySet):
    """
    People queryset defining the endpoint and the class to serialize the person object
    """
    endpoint = config.PEOPLE
    _klass = Person

    @property
    def people(self):
        """
        list of people filled up on construction of when fetching the data remotely
        """
        return self.items

    def __unicode__(self):
        return u'<PeopleQuerySet - {}>'.format(len(self))

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()
