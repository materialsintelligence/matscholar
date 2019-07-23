import requests
import datetime
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
from matscholar import SETTINGS
import warnings
import re
from pymongo import MongoClient
from tqdm import tqdm
import time

def clean_text(text):
    """ Cleans abstract text from scopus documents.

    Args:
        text (str): Unformatted abstract text.

    Returns:
        (str) Abstract text with formatting issues removed.

    """
    if text is None:
        return None
    try:
        cleaned_text = re.sub("© ([0-9])\w* The Author(s)*\.( )*", "", text)
        cleaned_text = re.sub("Published by Elsevier Ltd\.", "", cleaned_text)
        cleaned_text = re.sub("\n                        ", "", cleaned_text)
        cleaned_text = re.sub("\n                     ", "", cleaned_text)
        cleaned_text = " ".join("".join(cleaned_text.split("\n               ")).split())
        cleaned_text = cleaned_text.replace("Abstract ", '', 1)
        return cleaned_text
    except:
        return None


class ScopusCollector:

    def __init__(self, full_name=None, api_key=None, matscholar_user=None, matscholar_password=None):
        """
        A class to conveniently interface with the Scopus API for collection of
        abstracts.

        Args:
            name (str): Your full name. If this is None, the code will check
                if there is a "MATSCHOLAR_Name" setting. If so, it will use the
                name stored in your Matscholar settings.

            api_key (str): A String API key for accessing the Scopus API.
                This should be a *text mining key*. Please obtain your API key at
                http://dev.elsevier.com/myapikey.html. If this is None,
                the code will check if there is a "MATSCHOLAR_TEXT_MINING_KEY" setting.
                If so, it will use the key stored in your Matscholar settings.

            matscholar_user (str): A String username for the matscholar database. Make
                sure this is a read/write credential.  If this is None,
                the code will check if there is a "MATSCHOLAR_USER" setting.
                If so, it will use the username stored in your Matscholar settings.

            matscholar_password (str): A String password for the matscholar database. Make
                sure this is a read/write credential. If this is None,
                the code will check if there is a "MATSCHOLAR_PASSWORD" setting.
                If so, it will use the password stored in your Matscholar settings.
        """
        matscholar_host = "matstract-kve41.mongodb.net/test?w=majority"

        if full_name is not None:
            self.full_name = api_key
        else:
            self.full_name = SETTINGS.get("MATSCHOLAR_NAME", None)

        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = SETTINGS.get("MATSCHOLAR_TEXT_MINING_KEY", None)

        if matscholar_user is not None:
            self.matscholar_user = matscholar_user
        else:
            self.matscholar_user = SETTINGS.get("MATSCHOLAR_USER", None)

        if matscholar_password is not None:
            self.matscholar_password = matscholar_password
        else:
            self.matscholar_password = SETTINGS.get("MATSCHOLAR_PASSWORD", None)

        try:
            assert(None not in [self.full_name, self.api_key, self.matscholar_password, matscholar_user])
        except AssertionError as e:
            warnings.warn("Matscholar settings not configured. Please run `mscli configure` or "
                          "supply credentials as input arguments.")
            raise(e)
        user = self.matscholar_user
        uri = "mongodb+srv://{}:{}@{}".format(self.matscholar_user, self.matscholar_password, matscholar_host)
        self.client = MongoClient(uri=uri, connect=False)
        self.db = self.client["matscholar_staging"]


    def direct_download(self, url, format='xml', params=None):
        """
        Helper function to download a file and return its content from the Sopus API.

        Args:
            url: (str) The URL to be parsed.
            params: (dict, optional) Dictionary containing query parameters.  For required keys
                and accepted values see e.g.
                https://api.elsevier.com/documentation/AuthorRetrievalAPI.wadl

        Returns:
            resp : (byte-like object)
                The content of the file, which needs to be serialized.

        Raises:
            (HTTPError) If the status of the response is not ok.

        """

        header = {'Accept': 'application/{}'.format(format), 'X-ELS-APIKey': self.api_key}
        resp = requests.get(url, headers=header, params=params)
        resp.raise_for_status()
        return resp


    def verify_access(self):
        """ Confirms that the user is connected to a network with full access to Elsevier.
        i.e. the LBNL Employee Network

        Raises:
            HTTPError: If user is not connected to network with full-text subscriber access to Elsevier content.

        """
        try:
            self.direct_download("https://api.elsevier.com/content/article/doi/10.1016/j.actamat.2018.01.057?view=FULL")
        except requests.HTTPError:
            raise requests.HTTPError(" Cannot retreive full document from Elsevier API. \n \n"
                            "Please confrim that you're connected to a network or VPN with "
                            "full access to Scopus content.")


    #TODO: Make this a Matscholar API endpoint
    def retrieve_block_dois(self, issn, year):
        print("Retrieving block...")
        pass


    def process_block(self, issn, year, try_abstract_retrieval_api=False):
        """ Collects abstracts from Scopus using the Scopus Search API (and optionally the Abstract Retrieval API)
        and inserts them into the Matscholar DB.

        Raises:
            HTTPError: If user is not connected to network with full-text subscriber access to Elsevier content.

        """
        S = ScopusSearch("ISSN({}) AND PUBYEAR IS {}".format(issn, year))
        entries = []
        for result in S.results:
            date = datetime.datetime.now().isoformat()
            try:
                if result.description is None:
                    entries.append({"entry": result._asdict(),
                                    "completed": False,
                                    "error": "No Abstract!",
                                    "pulled_on": date,
                                    "pulled_by": self.full_name})
                else:
                    entries.append({"entry": result._asdict(),
                                    "completed": True,
                                    "pulled_on": date,
                                    "pulled_by": self.full_name})

            except requests.HTTPError as e:
                entries.append({"entry": result._asdict(),
                                "completed": False,
                                "error": str(e),
                                "pulled_on": date,
                                "pulled_by": self.full_name})

        return entries

    def contribute(self, max_block_size=1000, num_blocks=10):
        """
        Gets a incomplete year/journal combination from elsevier_log, queries for the corresponding
        dois, and downloads the corresponding xmls for each to the elsevier collection.

        Args:
            max_block_size ((:obj:`int`, optional)): maximum number of articles in block (~1s/article). Defaults to 100.
            num_blocks ((:obj:`int`, optional)): maximum number of blocks to run in session. Defaults to 1.
        """

        log = self.db.build_log
        build = self.db.build

        for i in range(num_blocks):
            time.sleep(3)  # to make sure we don't send more than 6 request / second on 16 cores (3 > 16/6)
            # Verify access at start of each block to detect dropped VPN sessions.
            self.verify_access()

            # Get list of all available blocks sorted from largest to smallest.
            available_blocks = log.find({"status": "incomplete",
                                         "num_articles": {"$lt": max_block_size}},
                                        ["year", "issn", "journal"]).limit(1).sort("num_articles", -1)

            # Break if no remaining blocks smaller than max_block_size
            if available_blocks.count() == 0:
                print("No remaining blocks with size <= {}.".format(max_block_size))
                break
            else:
                print("Blocks remaining = {}".format(min(num_blocks - i, available_blocks.count())))

            target = available_blocks[0]
            date = datetime.datetime.now().isoformat()
            log.update_one({"_id": target["_id"]},
                           {"$set": {"status": "in progress", "updated_by": user, "updated_on": date}})

            # Collect scopus for block
            if "journal" in target:
                print("Collecting entries for {}, {} (Block ID {})...".format(target.get("journal"),
                                                                              target.get("year"),
                                                                              target.get("_id")))
            else:
                print("Collecting entries for {}, {} (Block ID {})...".format(target.get("issn"),
                                                                              target.get("year"),
                                                                              target.get("_id")))
            dois = find_articles(year=target["year"], issn=target["issn"], get_all=True, apikey=apikey)
            new_entries = collect_entries_by_doi_search(dois, user, apikey=apikey)

            # Update log with number of articles for block
            num_articles = len(new_entries)
            log.update_one({"_id": target["_id"]},
                           {"$set": {"num_articles": num_articles}})

            # Insert entries into Matstract database
            print("Inserting entries into Matstract database...")
            for entry in tqdm(new_entries):
                build.replace_one({"doi": entry["doi"]}, entry, upsert=True)

            # Mark block as completed in log
            date = datetime.datetime.now().isoformat()
            log.update_one({"_id": target["_id"]},
                           {"$set": {"status": "complete", "completed_by": user, "completed_on": date,
                                     "updated_by": user, "updated_on": date}})
