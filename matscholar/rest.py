import requests
import json
import warnings
from os import environ

"""
This module provides classes to interface with the MatScholar REST
API.

To make use of the MatScholar API, you need to obtain an API key by 
contacting John Dagdelen at jdagdelen@berkeley.edu.
"""

__author__ = "John Dagdelen"
__credits__ = "Shyue Ping Ong, Shreyas Cholia, Anubhav Jain"
__copyright__ = "Copyright 2018, Materials Intelligence"
__version__ = "0.1"
__maintainer__ = "John Dagdelen"
__email__ = "jdagdelen@berkeley.edu"
__date__ = "October 3, 2018"


class Rester(object):
    """
    A class to conveniently interface with the Mastract REST interface.
    The recommended way to use MatstractRester is with the "with" context
    manager to ensure that sessions are properly closed after usage::

        with MatstractRester("API_KEY") as m:
            do_something

    MatstractRester uses the "requests" package, which provides for HTTP connection
    pooling. All connections are made via https for security.

    Args:
        api_key (str): A String API key for accessing the MaterialsProject
            REST interface. Please obtain your API key by emailing
            John Dagdelen at jdagdelen@berkeley.edu. If this is None,
            the code will check if there is a "MATSTRACT_API_KEY" environment variable.
            If so, it will use that environment variable. This makes
            easier for heavy users to simply add this environment variable to
            their setups and MatstractRester can then be called without any arguments.
        endpoint (str): Url of endpoint to access the Matstract REST
            interface. Defaults to the standard address, but can be changed to other
            urls implementing a similar interface.
    """

    def __init__(self, api_key=None,
                 endpoint="http://0.0.0.0:8080"):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = environ['MATERIALS_SCHOLAR_API_KEY']
        self.preamble = endpoint
        self.session = requests.Session()
        self.session.headers = {"x-api-key": self.api_key}

    def __enter__(self):
        """
        Support for "with" context.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Support for "with" context.
        """
        self.session.close()

    def _make_request(self, sub_url, payload=None, method="GET"):
        response = None
        url = self.preamble + sub_url
        try:
            if method == "POST":
                response = self.session.post(url, json=payload, verify=True)
            else:
                response = self.session.get(url, params=payload, verify=True)
            if response.status_code in [200, 400]:
                data = json.loads(response.text)
                if data["valid_response"]:
                    if data.get("warning"):
                        warnings.warn(data["warning"])
                    return data["response"]
                else:
                    raise MatScholarRestError(data["error"])

            raise MatScholarRestError("REST query returned with error status code {}"
                                     .format(response.status_code))

        except Exception as ex:
            msg = "{}. Content: {}".format(str(ex), response.content) \
                if hasattr(response, "content") else str(ex)
            raise MatScholarRestError(msg)

    def materials_search(self, positive, negative=None, ignore_missing=True, top_k=10):

        if not isinstance(positive, list):
            positive = [positive]
        if negative and not isinstance(negative, list):
            negative = [negative]
        method = "GET"
        sub_url = '/embeddings/matsearch/{}'.format(",".join(positive))
        payload = {'top_k': top_k, 'negative': ",".join(negative) if negative else None, 'ignore_missing': ignore_missing}

        return self._make_request(sub_url, payload=payload, method=method)

    def close_words(self, positive, negative=None, ignore_missing=True, top_k=10):

        if not isinstance(positive, list):
            positive = [positive]
        if negative and not isinstance(negative, list):
            negative = [negative]

        method = "GET"
        sub_url = '/embeddings/close_words/{}'.format(",".join(positive))
        payload = {'top_k': top_k, 'negative': ",".join(negative) if negative else None, 'ignore_missing': ignore_missing}

        return self._make_request(sub_url, payload=payload, method=method)

    def mentioned_with(self, material, words):

        method = "GET"
        sub_url = '/search/mentioned_with'
        payload = {
            'material': material,
            'words': " ".join(words)
        }

        return self._make_request(sub_url, payload=payload, method=method)


class MatScholarRestError(Exception):
    """
    Exception class for MatstractRester.
    Raised when the query has problems, e.g., bad query format.
    """
    pass
