import csv
import logging
import os


class CSVHandler:
    class MissingCSVFields(Exception):
        """
        Exception raised when fields are not passed to generate the CSV file
        """
        pass

    def __init__(self, items, fields=None, delimiter=',', quotechar='"', include_headers=True, file_path='output.csv'):
        """

        :param items: items to be dump to the csv file
        :param fields: map of the field names and attributes inside the items following {'header_name':'attribute_name'}
        :param delimiter: csv delimited [Default: ',']
        :param quotechar: csv quotechar [Default: '"']
        :param include_headers: boolean to include headers or not [Default: True]
        :param file_path: csv file path [Default: 'output.csv']
        """
        self.log = logging.getLogger(self.__class__.__name__)

        self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', file_path)
        if not fields:
            raise CSVHandler.MissingCSVFields

        headers = fields.keys()
        items_fields = fields.values()

        rows = []
        for item in items:
            rows.append([str(getattr(item, field)) if field else '' for field in items_fields])

        with open(self.file_path, mode='w') as csv_file:
            writer = csv.writer(csv_file, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)
            if include_headers:
                logging.debug("Writting headers to file %s", headers)
                writer.writerow(headers)
            for row in rows:
                logging.debug("Writting row to file %s", row)
                writer.writerow(row)

            logging.info("CSV file generated successfuly: %s", self.file_path)
