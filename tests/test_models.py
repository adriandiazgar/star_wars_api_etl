import json
import os
from unittest import TestCase

from mock import patch

import config
from models import BaseQuerySet, PeopleQuerySet, SpeciesQuerySet, Person, Species


class TestModels(TestCase):
    def test_default_constructor(self):
        base_query_set = BaseQuerySet()
        self.assertEqual(base_query_set.items, [])
        self.assertEqual(base_query_set.foreign_keys, [])

    def test_constructor_with_predefined_items(self):
        base_query_set = BaseQuerySet(items=[1, 2, 3], foreign_keys={'field_name': 'querysetclass'})
        self.assertEqual(base_query_set.items, [1, 2, 3])
        self.assertEqual(base_query_set.foreign_keys, {'field_name': 'querysetclass'})

    @patch('utils.Requester.serialize')
    @patch('utils.Requester._Requester__get')
    def test_get_all_query(self, mock_get, mock_serialize):
        class DummyQuerySet(BaseQuerySet):
            endpoint = 'dummy'

        mock_get.return_value = {'results': [{'key': 'value'}]}
        mock_serialize.return_value = lambda x: x
        query_set = DummyQuerySet()
        query_set.get_all()
        mock_get.assert_called_once()
        mock_get.assert_called_with('{}/dummy'.format(config.SWAPI_BASE_URL))
        mock_serialize.assert_called_with(items=[{'key': 'value'}])

    @patch('utils.Requester.serialize')
    @patch('utils.Requester._Requester__get')
    def test_get_by_url(self, mock_get, mock_serialize):
        class DummyQuerySet(BaseQuerySet):
            endpoint = 'dummy'

        mock_get.return_value = [{'key': 'value'}]
        mock_serialize.return_value = lambda x: x
        query_set = DummyQuerySet()
        query_set.get_by_url("http://fakeurl/object/1")
        mock_get.assert_called_once()
        mock_get.assert_called_with('http://fakeurl/object/1')
        mock_serialize.assert_called_with(items=[{'key': 'value'}])

    @patch('utils.Requester._Requester__get')
    def test_get_all_query_person_query_set(self, mock_get):
        fixtures_people_page1_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  'fixtures/people_page_1.json')
        fixtures_people_page2_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  'fixtures/people_page_2.json')
        with open(fixtures_people_page1_path, 'r') as f:
            file1_content = f.read()
        with open(fixtures_people_page2_path, 'r') as f:
            file2_content = f.read()

        mock_get.side_effect = [json.loads(file1_content), json.loads(file2_content)]
        query_set = PeopleQuerySet()
        result = query_set.get_all()
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(len(result), 12)
        self.assertEqual(len(result.items), 12)
        self.assertEqual(len(result.people), 12)

        self.assertEqual(result.items[0].name, 'Luke Skywalker')
        self.assertEqual(result.items[0].films_count, 5)
        self.assertEqual(result.items[0].height, 172)
        self.assertEqual(result.items[0].species, 'https://swapi.co/api/species/1/')

        self.assertEqual(result.items[1].name, 'C-3PO')
        self.assertEqual(result.items[1].films_count, 6)
        self.assertEqual(result.items[1].height, 167)
        self.assertEqual(result.items[1].species, 'https://swapi.co/api/species/2/')

        mock_get.assert_any_call('https://swapi.co/api/people')
        mock_get.assert_any_call('https://swapi.co/api/people/?page=2')

    def test_order_by_films_count(self):
        query_set = PeopleQuerySet(items=
        [
            Person(name='secondary_actor', height='100', films=[1], species=['species1']),
            Person(name='main_actor', height='90', films=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], species=['species2'])
        ])

        ordered_results = query_set.order_by(attribute='films_count')
        self.assertEqual(ordered_results.items[0].name, 'main_actor')
        self.assertEqual(ordered_results.items[0].films_count, 10)
        self.assertEqual(ordered_results.items[0].height, 90)
        self.assertEqual(ordered_results.items[0].species, 'species2')

        self.assertEqual(ordered_results.items[1].name, 'secondary_actor')
        self.assertEqual(ordered_results.items[1].films_count, 1)
        self.assertEqual(ordered_results.items[1].height, 100)
        self.assertEqual(ordered_results.items[1].species, 'species1')

    @patch('utils.Requester._Requester__get')
    def test_get_by_url_query_spieces_query_set(self, mock_get):
        fixtures_speices_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/species_1.json')
        with open(fixtures_speices_path, 'r') as f:
            file1_content = f.read()

        mock_get.return_value = json.loads(file1_content)
        query_set = SpeciesQuerySet()
        result = query_set.get_by_url("https://myfakeurl/species/1")
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(result.name, 'Human')
        mock_get.assert_any_call('https://myfakeurl/species/1')

    def test_unicode_string_and_repr_PeopleQuerySet(self):
        query_set = PeopleQuerySet(items=
        [
            Person(name='secondary_actor', height='100', films=[1], species=['species1']),
            Person(name='main_actor', height='90', films=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], species=['species2'])
        ])

        self.assertEqual(repr(query_set), '<PeopleQuerySet - 2>')
        self.assertEqual(str(query_set), '<PeopleQuerySet - 2>')
        self.assertEqual(u"%s" % query_set, '<PeopleQuerySet - 2>')

    def test_unicode_string_and_repr_SpeciesQuerySet(self):
        query_set = SpeciesQuerySet(items=
        [
            Species(name='species1'),
            Species(name='species2'),
        ])

        self.assertEqual(repr(query_set), '<SpeciesQuerySet - 2>')
        self.assertEqual(str(query_set), '<SpeciesQuerySet - 2>')
        self.assertEqual(u"%s" % query_set, '<SpeciesQuerySet - 2>')

    def test_species_model(self):
        species_to_test = Species(name='myspeciesname')

        self.assertEqual(species_to_test.name, 'myspeciesname')

        self.assertEqual(repr(species_to_test), '<Species - myspeciesname>')
        self.assertEqual(str(species_to_test), '<Species - myspeciesname>')
        self.assertEqual(u"%s" % species_to_test, '<Species - myspeciesname>')

    def test_person_model(self):
        person_to_test = Person(name='main_actor', height='90', films=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                species=['species2'])

        self.assertEqual(person_to_test.name, 'main_actor')
        self.assertEqual(person_to_test.height, 90)
        self.assertEqual(person_to_test.films_count, 10)
        self.assertEqual(person_to_test.species, 'species2')

        self.assertEqual(repr(person_to_test), '<Person - main_actor>')
        self.assertEqual(str(person_to_test), '<Person - main_actor>')
        self.assertEqual(u"%s" % person_to_test, '<Person - main_actor>')

    def test_queryset_getitem_method(self):
        query_set = PeopleQuerySet(items=
        [
            Person(name='secondary_actor', height='100', films=[1], species=['species1']),
            Person(name='main_actor', height='90', films=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], species=['species2']),
            Person(name='another_actor', height='50', films=[1, 2, 3, 4], species=['species1'])
        ])

        slice_of_one_person = query_set[0:1]
        self.assertEqual(len(slice_of_one_person), 1)
        self.assertEqual(slice_of_one_person.people[0].name, 'secondary_actor')
        self.assertEqual(slice_of_one_person.people[0].height, 100)
        self.assertEqual(slice_of_one_person.people[0].films_count, 1)
        self.assertEqual(slice_of_one_person.people[0].species, 'species1')

        slice_of_two_people = query_set[0:2]
        self.assertEqual(len(slice_of_two_people), 2)
        self.assertEqual(slice_of_two_people.people[0].name, 'secondary_actor')
        self.assertEqual(slice_of_two_people.people[0].height, 100)
        self.assertEqual(slice_of_two_people.people[0].films_count, 1)
        self.assertEqual(slice_of_two_people.people[0].species, 'species1')

        self.assertEqual(slice_of_two_people.people[1].name, 'main_actor')
        self.assertEqual(slice_of_two_people.people[1].height, 90)
        self.assertEqual(slice_of_two_people.people[1].films_count, 10)
        self.assertEqual(slice_of_two_people.people[1].species, 'species2')

        first_person = query_set[1]
        self.assertEqual(first_person.name, 'main_actor')
        self.assertEqual(first_person.height, 90)
        self.assertEqual(first_person.films_count, 10)
        self.assertEqual(first_person.species, 'species2')

        with self.assertRaises(NotImplementedError):
            query_set[(1, 2)]

        with self.assertRaises(TypeError):
            query_set['INVALID']

    def test_queryset_iter_method(self):
        query_set = PeopleQuerySet(items=
        [
            Person(name='secondary_actor', height='100', films=[1], species=['species1']),
            Person(name='main_actor', height='90', films=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], species=['species2']),
            Person(name='another_actor', height='50', films=[1, 2, 3, 4], species=['species1'])
        ])
        expected = [
            Person(name='secondary_actor', height='100', films=[1], species=['species1']),
            Person(name='main_actor', height='90', films=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], species=['species2']),
            Person(name='another_actor', height='50', films=[1, 2, 3, 4], species=['species1'])
        ]
        for idx, person in enumerate(query_set):
            self.assertEqual(expected[idx].name, person.name)
            self.assertEqual(expected[idx].height, person.height)
            self.assertEqual(expected[idx].films_count, person.films_count)
            self.assertEqual(expected[idx].species, person.species)

    @patch('utils.Requester._Requester__get')
    def test_resolve_foreign_keys(self, mock_get):
        query_set = PeopleQuerySet(items=
        [
            Person(name='secondary_actor', height='100', films=[1], species=['https://myfakeurl/species/1']),
        ], foreign_keys={'species': SpeciesQuerySet()})

        fixtures_species_1 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          'fixtures/species_1.json')

        with open(fixtures_species_1, 'r') as f:
            file1_content = f.read()

        mock_get.return_value = json.loads(file1_content)

        self.assertEqual(query_set.people[0].name, 'secondary_actor')
        self.assertEqual(query_set.people[0].height, 100)
        self.assertEqual(query_set.people[0].films_count, 1)
        self.assertEqual(query_set.people[0].species, 'https://myfakeurl/species/1')

        query_set.resolve_foreign_keys()

        self.assertEqual(query_set.people[0].name, 'secondary_actor')
        self.assertEqual(query_set.people[0].height, 100)
        self.assertEqual(query_set.people[0].films_count, 1)
        self.assertEqual(query_set.people[0].species, 'Human')

        mock_get.assert_called_once()
        mock_get.assert_called_with('https://myfakeurl/species/1')
