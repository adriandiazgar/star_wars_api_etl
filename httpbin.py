import logging

import requests

import config

log = logging.getLogger("HTTPBin")


class HTTPBin:
    """
    Class to interact with HTTPBIN.org page
    """

    class FileIntegrityError(Exception):
        pass

    def send_file(self, file):
        """
        Send file to httpbin.org, if the file is not uploaded correctly it will raise an Exception
        :param file: file path
        """
        response = requests.post("{}/{}".format(config.HTTPBIN_BASE_URL, config.HTTPBIN_FILE_ENDPOINT),
                                 files={'file': open(file, mode='rb')})
        response.raise_for_status()
        self.__check_response(response=response.json(), file=file)

    def __check_response(self, response, file):
        """
        Check response, httpbin.org will echo the sent data, so file integrity can be checked, if integrity check fails
        exception will be raised
        :param response: response from httpbin.org
        :param file: file path
        """
        response_file_content = response.get('files', {}).get('file').replace('\n', '').replace('\r', '')
        file_content = ''.join(open(file, mode='r').readlines()).replace('\n', '').replace('\r', '')
        if response_file_content != file_content:
            raise HTTPBin.FileIntegrityError(
                "Issue uploading file to httpbin, content recieved on their end is different Local: %s vs Remote: %s",
                file_content, response_file_content)

        logging.info("Intergity of uploaded file OK")
        logging.info("File successfully uploaded to %s/post", config.HTTPBIN_BASE_URL)
