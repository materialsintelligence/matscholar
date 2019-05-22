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

    def __init__(self, api_key=None, endpoint=None):
        self.api_key = api_key if api_key else environ['MATERIALS_SCHOLAR_API_KEY']
        self.preamble = endpoint if endpoint else "http://0.0.0.0:8080" #environ['MATERIALS_SCHOLAR_ENDPOINT']
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
        print(url)
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
        """
        Given input strings or lists of positive and negative words / phrases, returns a ranked list of materials with
        corresponding scores and numbers of mentions
        :param positive: a string or a list of strings used as a positive search criterion
        :param negative: a string or a list of strings used as a negative search criterion
        :param ignore_missing: if True, ignore words missing from the embedding vocabulary, otherwise generate "guess"
        embeddings
        :param top_k: number of top results to return (10 by default)
        :return: a dictionary with the following keys ["materials", "counts", "scores", "positive", "negative",
                                                                    "original_negative", "original_positive"]
        """

        if not isinstance(positive, list):
            positive = [positive]
        if negative and not isinstance(negative, list):
            negative = [negative]
        method = "GET"
        sub_url = '/embeddings/matsearch/{}'.format(",".join(positive))
        payload = {'top_k': top_k, 'negative': ",".join(negative) if negative else None, 'ignore_missing': ignore_missing}

        return self._make_request(sub_url, payload=payload, method=method)

    def close_words(self, positive, negative=None, ignore_missing=True, top_k=10):
        """
        Given input strings or lists of positive and negative words / phrases, returns a list of most similar words /
        phrases according to cosine similarity
        :param positive: a string or a list of strings used as positive contributions to the cumulative embedding
        :param negative: a string or a list of strings used as negative contributions to the cumulative embedding
        :param ignore_missing: if True, ignore words missing from the embedding vocabulary, otherwise generate "guess"
        embeddings
        :param top_k: number of top results to return (10 by default)
        :return: a dictionary with the following keys ["close_words", "scores", "positive", "negative",
                                                                    "original_negative", "original_positive"]
        """

        if not isinstance(positive, list):
            positive = [positive]
        if negative and not isinstance(negative, list):
            negative = [negative]

        method = "GET"
        sub_url = '/embeddings/close_words/{}'.format(",".join(positive))
        payload = {'top_k': top_k, 'negative': ",".join(negative) if negative else None, 'ignore_missing': ignore_missing}

        return self._make_request(sub_url, payload=payload, method=method)

    def get_embedding(self, wordphrases, ignore_missing=True):
        """
        Returns the embedding(s) for the supplied wordphrase. If the wordphrase is a string, returns a single embedding
        vector as a list. If the wordphrase is a list of string, returns a matrix with each row corresponding to a single
        (potentially cumulative) embedding. If the words (after pre-processing) do not have embeddings and
        ignore_missing is set to True, a list of all 0s is returned
        :param wordphrases: a string or a list of strings
        :param ignore_missing: if True, will ignore missing words, otherwise will guess embeddings based on
        string similarity
        :return: a dictionary with following keys ["original_wordphrases", "processed_wordphrases", "embeddings"]
        """

        if isinstance(wordphrases, list):
            method = "POST"
            sub_url = '/embeddings'
            payload = {
                'wordphrases': wordphrases,
                'ignore_missing': ignore_missing
            }
        else:
            method = "GET"
            sub_url = '/embeddings/{}'.format(wordphrases)
            payload = {
                'ignore_missing': ignore_missing
            }

        return self._make_request(sub_url, payload=payload, method=method)

    def materials_map(self, highlight, limit=None, ignore_missing=True, number_to_substring=False, dims=2):
        """
        Returns data for a plotly dash scatter plot, highlighted according to cosine similarity to highlight
        :param highlight: a string or a list of strings according to which materials should be highlighted
        :param limit: number of top materials (sorted by number of mentions) to show
        :param ignore_missing: if True, will ignore missing words, otherwise will guess embeddings based on
        string similarity
        :param number_to_substring: if true, will convert numbers in chemical formula to substrings
        :param dims: 2 or 3, determines if the map is 2D or 3D
        :return: a dictionary with following keys: ["x", "y", "text", "marker"]
        """

        if highlight is not None and not isinstance(highlight, list):
            highlight = [highlight]
        method = "GET"
        sub_url = '/materials_map'
        payload = {'highlight': highlight,
                   'limit': limit,
                   'ignore_missing': ignore_missing,
                   'number_to_substring': number_to_substring,
                   'dims': dims}

        return self._make_request(sub_url, payload=payload, method=method)
      
    def search_ents(self, query):
        """
        Get the entities in each document associated with a given query

        :param query: dict; e.g., {'material': ['GaN', '-InN']), 'application': ['LED']}
        :return: list of dicts; each dict represents a document and contains the extracted entities
        """

        method = "POST"
        sub_url = "/ent_search"
        payload = query

        return self._make_request(sub_url, payload=payload, method=method)

    def get_journals(self, query):
        '''

        :param query: string: a paragraph
        :return: list: [['journal name', 'cosine similarity'], ...]
        '''

        method = 'POST'
        sub_url = '/journal_suggestion'
        payload = {'abstract': query}

        return self._make_request(sub_url, payload=payload, method=method)


    def get_summary(self, query):
        """
        Get a summary of the entities associated with a given query

        :param query: dict; e.g., {'material': ['GaN', '-InN']), 'application': ['LED']}
        :return: dict; a summary dict with keys for each entity type
        """

        method = "POST"
        sub_url = "/ent_search/summary"
        payload = query

        return self._make_request(sub_url, payload=payload, method=method)

    def get_similar_materials(self, material):
        """
        Finds the most similar compositions in the corpus.

        :param material: string; a chemical composition
        :return: list; the most similar compositions
        """
        method = "GET"
        sub_url = '/materials/similar/{}'.format(material)
        return self._make_request(sub_url, method=method)

    def get_ner_tags(self, docs, return_type="concatenated"):
        """
        Performs Named Entity Recognition.

        :param docs: list; a list of documents; each document is represented as a single string
        :param return_type: string; output format, can be "iob", "concatenated", or "normalized"
        :return: list; tagged documents
        """

        method = "POST"
        sub_url = "/ner"
        payload = {
            "docs": docs,
            "return_type": return_type
        }
        return self._make_request(sub_url, payload=payload, method=method)

    def materials_search_ents(self, entities, elements, cutoff=None):
        """
        Finds materials that co-occur with specified entities. The returned materials can be screened
        by specifying elements that must be included/excluded from the stoichiometry.

        :param entities: list of strings; each string is a property or application
        :param elements: list of strings; each string is a chemical element. Materials
        will only be returned if they contain these elements; the opposite can also be
        achieved - materials can be removed from the returned list by placing a negative
        sign in from of the element, e.g., "-Ti"
        :param cutoff: int or None; if int, specifies the number of materials to
        return; if None, returns all materials
        :return: list; a list of chemical compositions
        """

        method = "POST"
        sub_url = "/search/material_search"
        payload = {
            "entities": entities,
            "elements": elements,
            "cutoff": cutoff
        }
        return self._make_request(sub_url, payload=payload, method=method)

    def search_text_with_ents(self, text, filters, cutoff=None):
        """
        Search abstracts by text with filters for entities
        :param text: string; text to search
        :param filters: dict; e.g., {'material': ['GaN', '-InN']), 'application': ['LED']}
        :param cutoff: int or None; if int, specifies the number of matches to
        return; if None, returns all matches
        :return: list; a list of chemical compositions
        """

        method = "POST"
        sub_url = "/search"
        filters['text'] = text
        payload = {
            "query": filters,
            "limit": cutoff
        }

        return self._make_request(sub_url, payload=payload, method=method)


class MatScholarRestError(Exception):
    """
    Exception class for MatstractRester.
    Raised when the query has problems, e.g., bad query format.
    """
    pass
