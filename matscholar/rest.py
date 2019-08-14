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
__credits__ = "Leigh Weston, Amalie Trewartha, Vahe Tshitoyan"
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
        self.preamble = endpoint if endpoint else environ['MATERIALS_SCHOLAR_ENDPOINT']
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

    def __search(self,group_by,entities,text=None,elements=None,top_k=10):
        method = "POST"
        sub_url = "/search/"
        query = {'entities':entities,'group_by':group_by,'limit':top_k}
        if text:
            query['text'] = text
        if elements:
            query['elements'] = elements

        return self._make_request(sub_url, payload=query, method=method)

    def abstracts_search(self,entities,text=None,elements=None,top_k=10):
        """
        Search for abstracts
        :param entities: string or list of strings; entities to filter by
        :param text: string; text to search
        :param elements: string or list of strings; filter by elements in materials
        :param top_k: int or None; if int, specifies the number of matches to
        return; if None, returns all matches
        :return: list; a list abstracts matching criteria
        """

        group_by = "abstracts"
        return self.__search(group_by,entities,text,elements,top_k)

    def materials_search(self,entities,text=None,elements=None,top_k=10):
        """
        Search for materials
        :param entities: string or list of strings; entities to filter by
        :param text: string; text to search
        :param elements: string or list of strings; filter by elements in materials
        :param top_k: int or None; if int, specifies the number of matches to
        return; if None, returns all matches
        :return: list; a list abstracts matching criteria
        """

        group_by = "materials"
        return self.__search(group_by,entities,text,elements,top_k)

    def entities_search(self,entities,text=None,elements=None,top_k=10):
        group_by = "entities"
        return self.__search(group_by,entities,text,elements,top_k)

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
      
    def get_journals(self, query):
        '''

        :param query: string: a paragraph
        :return: list: [['journal name', 'cosine similarity'], ...]
        '''

        method = 'POST'
        sub_url = '/journal_suggestion'
        payload = {'abstract': query}

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

    def get_abstract_count(self):
        """
        Get the total count of abstracts in the database
        """

        method = "GET"
        sub_url = "/abstract_count"

        return self._make_request(sub_url,method=method)

    def classify_relevance(self, docs, decision_boundary=0.5):
        """
        Determine whether or not a document relates to inorganic material science.

        :param docs: list of strings; the documents to be classified
        :param decision_boundary: float; decision boundary for the classifier
        :return: list; classification labels for each doc (1 or 0)
        """
        method = "POST"
        sub_url = "/relevance"
        payload = {
            "docs": docs,
            "decision_boundary": decision_boundary
        }

        return self._make_request(sub_url, payload=payload, method=method)


class MatScholarRestError(Exception):
    """
    Exception class for MatstractRester.
    Raised when the query has problems, e.g., bad query format.
    """
    pass

