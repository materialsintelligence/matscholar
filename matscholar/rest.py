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
        print(url)
        try:
            if method == "POST":
                response = self.session.post(url, json=payload, verify=True)
            else:
                response = self.session.get(url, params=payload, verify=True)

            print(response.status_code)
            if response.status_code in [200, 400]:
                data = json.loads(response.text)
                if isinstance(data, dict):
                    if data.get("warning"):
                        warnings.warn(data["warning"])
                    return data
                return data
            else:
                raise MatScholarRestError(response)

        except Exception as ex:
            msg = "{}. Content: {}".format(str(ex), response.content) \
                if hasattr(response, "content") else str(ex)
            raise MatScholarRestError(msg)

    def __search(self, group_by, entities, text=None, elements=None, top_k=10):
        method = "POST"
        sub_url = "/search"
        query = {'entities': entities, 'group_by': group_by, 'limit': top_k}
        if text:
            query['text'] = text
        if elements:
            query['elements'] = elements

        return self._make_request(sub_url, payload=query, method=method)

    def abstracts_search(self, entities, text=None, elements=None, top_k=10):
        """
        Search for abstracts by entities and text filters.

        Args:

            entities: dict of entity lists (list of str) to filter by. Keys are
              singular snake case for each of the entity types (material,
              property, descriptor, application, synthesis_method,
              structure_phase_label, characterization_method)

            text: english text, which gets searched on via Elasticsearch.

            elements: string or list of strings; filter by elements in materials

            top_k: (int or None) if int, specifies the number of matches to
                return; if None, returns all matches.

        Returns:
            List of entries (dictionaries) with abstracts, entities, and metadata.
        """

        method = "POST"
        sub_url = "/entries"
        query = {'query': {'entities': entities, 'text': text},
                 'limit': top_k}

        return self._make_request(sub_url, payload=query, method=method)

    def materials_search(self, entities, text=None, elements=None, top_k=10):
        """
        Search for materials

        Args:

            entities: dict of entity lists (list of str) to filter by. Keys are
              singular snake case for each of the entity types (material,
              property, descriptor, application, synthesis_method,
              structure_phase_label, characterization_method)

            text: english text, which gets searched on via Elasticsearch.

            elements: string or list of strings; filter by elements in materials

            top_k: (int or None) if int, specifies the number of matches to
                return; if None, returns all matches.

        Returns:
            List of entries (dictionaries) with abstracts, entities, and metadata.
        """

        method = "POST"
        sub_url = "/materials"
        query = {'entities': entities, 'text': text}

        return self._make_request(sub_url, payload=query, method=method)

    def entities_search(self, entities, text=None, elements=None, top_k=10):

        method = "POST"
        sub_url = "/entities"
        query = {'query': {'entities': entities, 'text': text},
                 'limit': top_k}

        return self._make_request(sub_url, payload=query, method=method)

    def dois_search(self, entities, text=None, elements=None, top_k=None):
        """
        Search for dois

        Args:

            entities: dict of entity lists (list of str) to filter by. Keys are
              singular snake case for each of the entity types (material,
              property, descriptor, application, synthesis_method,
              structure_phase_label, characterization_method)

            text: english text, which gets searched on via Elasticsearch.

            elements: string or list of strings; filter by elements in materials

            top_k: (int or None) if int, specifies the number of matches to
                return; if None, returns all matches.

        Returns:
            List of of dois matching criteria.

        """

        method = "POST"
        sub_url = "/entities/dois"
        query = {'query': {'entities': entities, 'text': text},
                 'limit': top_k}

        return self._make_request(sub_url, payload=query, method=method)

    def close_words(self, positive, negative=None, ignore_missing=True, top_k=10):
        """
        Given input strings or lists of positive and negative words / phrases, returns a list of most similar words /
        phrases according to cosine similarity

        Args:
            positive: a string or a list of strings used as positive contributions to the cumulative embedding
            negative: a string or a list of strings used as negative contributions to the cumulative embedding
            ignore_missing: number of top results to return (10 by default)
            top_k: a dictionary with the following keys ["close_words", "scores", "positive", "negative",
                                                                    "original_negative", "original_positive"]

        Returns:
            A list of similar words to the provided wordphrase expression.
        """

        if not isinstance(positive, list):
            positive = [positive]
        if negative and not isinstance(negative, list):
            negative = [negative]

        method = "GET"
        sub_url = '/embeddings/close_words/{}'.format(",".join(positive))
        payload = {'top_k': top_k, 'negative': ",".join(
            negative) if negative else None, 'ignore_missing': ignore_missing}

        return self._make_request(sub_url, payload=payload, method=method)

    def get_embedding(self, wordphrase, ignore_missing=True):
        """
        Returns the embedding(s) for the supplied wordphrase. If the wordphrase
        is a string, returns a single embedding vector as a list. If the
        wordphrase is a list of string, returns a matrix with each row
        corresponding to a single (potentially cumulative) embedding. If the
        words (after pre-processing) do not have embeddings and ignore_missing
        is set to True, a list of all 0s is returned

        Args:
            wordphrase: a string or a list of strings

            ignore_missing: if True, will ignore missing words,
              otherwise will guess embeddings based on string similarity

        Returns:

            a dictionary with following keys ["original_wordphrases",
              "processed_wordphrases", "embeddings"]

        """

        if isinstance(wordphrase, list):
            method = "POST"
            sub_url = '/embeddings'
            payload = {
                'wordphrases': wordphrase,
                'ignore_missing': ignore_missing
            }
        else:
            method = "GET"
            sub_url = '/embeddings/{}'.format(wordphrase)
            payload = {
                'ignore_missing': ignore_missing
            }

        return self._make_request(sub_url, payload=payload, method=method)

    def get_journals(self):
        """
        Get a list of all distinct journals in the db.

        Returns:
            List of distinct journal names
        """

        method = "GET"
        sub_url = "/stats/journals"
        return self._make_request(sub_url, method=method)

    def get_ner_tags(self, document, concatenate=True, normalize=False):
        """
        Performs Named Entity Recognition on a document, labeling words that fall
          into the 7 Matscholar entity types: material, property, application,
          descriptor, structure/phase label, characterization method, and synthesis
          method.

        Args:

            document: str

            concatenate: bool, set to True if you want concurrent entities
              combined into a single token-entity.

            normalize: bool, set to True if you want entites returned in their
              normalized form (XRD = x-ray diffraction = xray diffraction)

        Returns:
            List of token-tag pairs.

        """

        method = "POST"
        sub_url = "/nlp/extract_entities"
        payload = {
            "document": document,
            "concatenate": concatenate,
            "normalize": normalize
        }
        return self._make_request(sub_url, payload=payload, method=method)

    def get_db_stats(self):
        """
         Get the statistics about the Matscholar db.

        Returns:
            dictionary of stats. e.g
              {'abstract_count': 4941666,
               'entities_count': 518026,
               'materials_count': 290952}

        """

        method = "GET"
        sub_url = "/stats/"

        return self._make_request(sub_url, method=method)

    def classify_relevance(self, docs, decision_boundary=0.5):
        """
        Determine whether or not a document relates to inorganic material science.
        Args:
            docs: list of strings; the documents to be classified
            decision_boundary: float; decision boundary for the classifier

        Returns:
            list; classification labels for each doc (1 or 0)
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
