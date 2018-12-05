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

    supported_fields = ['_id', 'title', 'authors', 'year',
                        'abstract', 'doi', 'journal', 'keywords',
                        'link', 'source', 'material', 'property',
                        'application', 'descriptor', 'phase',
                        'characterization_method', 'synthesis_method']

    default_fields = ['_id', 'title', 'authors', 'year',
                      'abstract', 'doi', 'journal', 'keywords',
                      'link']

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

    def get_entries(self, ids, id_type='id', fields=()):
        """
        Gets entries from the Matstract DB via id or doi using the Matstract REST
        interface. Generally used by other methods for more specific queries.

        Format of REST return is *always* a list of dict (regardless of the
        number of pieces of data returned. The general format is as follows:

        [{"entry_id": entry_id, "field_name" : value}, ...]

        Args:
           ids (list): A LIST of Matstract entry id strings (for specific papers).
               e.g.
               ['a235l12kh1242'] or ['doi_1', 'doi_2', 'doi_3']
           fields (list): list of fields to be obtained. Should be one of the
               MatstractRester.supported_fields. Leave as empty list for a
               general list of useful fields.
        """
        sub_url = "/abstracts"
        url_size = len("".join(ids + fields))
        # For small queries under the url character limit, use a GET request
        if url_size < 1500 and not len(fields):
            fields = self.default_fields
            sub_url += "/id/%s" % (",".join(ids))
            method = 'GET'
        # For larger queries over the url character limit, use a POST request
        else:
            method = 'POST'
            if any([field not in self.supported_fields for field in fields]):
                raise MatScholarRestError('unsupported field')
        payload = {
            'ids': ids,
            'id_type': id_type,
            'fields': fields
        }
        return self._make_request(sub_url, payload=payload, method=method)

    def get_entries_by_doi(self, dois, fields=()):
        """
        Gets entries from the Matstract DB via dois using the Matstract REST
        interface. Generally used by other methods for more specific queries.

        Format of REST return is *always* a list of dict (regardless of the
        number of pieces of data returned. The general format is as follows:

        [{"entry_id": entry_id, "field_name" : value}, ...]

        Args:
            ids (list): A list of Matstract entry id strings (for specific papers).
                e.g. ['a235l12kh1242', '2351kjh1kh21l']
            field (list): list of fields to be obtained. Should be one of the
                MatstractRester.supported_fields. Leave as empty list for a
                general list of useful fields.
        """
        sub_url = "/abstracts"
        if len(",".join(dois)) < 1500 and not len(fields):
            fields = self.default_fields
            sub_url += "/%s" % (",".join(dois))
            method = 'GET'
        else:
            method = 'POST'
            if any([field not in self.supported_fields for field in fields]):
                raise MatScholarRestError('Unsupported field supplied. Supported fields are: {}'.format(self.supported_fields))
        payload = {
            'dois': dois,
            'fields': fields
        }
        return self._make_request(sub_url, payload=payload, method=method)

    def search(self, query, limit):
        base_query = {
                         "text": "",
                         "material": {
                             "positive": [],
                             "negative": []
                         },
                         "property": {
                             "positive": [],
                             "negative": []
                         },
                         "application": {
                             "positive": [],
                             "negative": []
                         },
                         "descriptor": {
                             "positive": [],
                             "negative": []
                         },
                         "characterization": {
                             "positive": [],
                             "negative": []
                         },
                         "synthesis": {
                             "positive": [],
                             "negative": []
                         },
                         "phase": {
                             "positive": [],
                             "negative": []
                         },
                        "keywords": {
                            "positive": [],
                            "negative": []
            }
                     }
        for key in query:
            if key == "text":
                base_query["text"] = query["text"]
            elif key in self.supported_fields:
                for item in query[key]:
                    if item[0] == "-":
                        base_query[key]["negative"].append(item[1::])
                    else:
                        base_query[key]["positive"].append(item)
            else:
                raise MatScholarRestError("{} is not a valid search field".format(key))

        query = base_query

        sub_url = '/search'
        payload = {
            'query': query,
            'limit': limit
        }

        return self._make_request(sub_url, payload=payload, method='POST')

    def test(self, message):
        method = 'GET'
        sub_url = '/test/' + message
        return self._make_request(sub_url, method=method)

    def materials_search(self, positive, negative=None, ignore_missing=True, top_k=10):

        method = "GET"
        sub_url = '/embeddings/matsearch/{}'.format(positive)
        payload = {'top_k': top_k, 'negative': negative, 'ignore_missing': ignore_missing}

        return self._make_request(sub_url, payload=payload, method=method)

    def close_words(self, positive, negative=None, ignore_missing=True, top_k=10):

        method = "GET"
        sub_url = '/embeddings/close_words/{}'.format(positive)
        payload = {'top_k': top_k, 'negative': negative, 'ignore_missing': ignore_missing}

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
