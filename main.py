from csv_handler import CSVHandler
from httpbin import HTTPBin
from models import PeopleQuerySet, SpeciesQuerySet


def main():
    all_people_query_set = PeopleQuerySet(foreign_keys={'species': SpeciesQuerySet()}).get_all()
    top_10_people_by_appearances = all_people_query_set.order_by('films_count')[0:10]
    top_10_people_by_appearances_order_by_height = top_10_people_by_appearances.order_by('height')
    top_10_people_by_appearances_order_by_height.resolve_foreign_keys()

    csv_file = CSVHandler(items=top_10_people_by_appearances_order_by_height.items,
                          fields={'name': 'name', 'species': 'species', 'height': 'height',
                                  'appearances': 'films_count'})

    HTTPBin().send_file(file=csv_file.file_path)


if __name__ == '__main__':
    main()
