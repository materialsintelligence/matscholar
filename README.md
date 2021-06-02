<img src="docs/logo.png" alt="matscholar logo" width="800px">

`matscholar` (Materials Scholar) is a Python library for materials-focused natural language 
processing (NLP). It is maintained by a team of researchers at UC Berkeley and Lawrence Berkeley 
National Laboratory as part of a project funded by the Toyota Research Institute.


The Matscholar API is under a major redesign and is currently not available. If you wish to use our NER models for named entity recognition (now housed in the [LBNLP repo](https://github.com/lbnlp/lbnlp)), you can run them locally by following the [instructions here](https://lbnlp.github.io/lbnlp/pretrained/). 

This library provides a Python interface for interacting with the Materials Scholar API, performing
basic NLP tasks on scientific text, and example notebooks on using these tools for materials 
discovery and design.

Documentation for the API can be found in this readme, as well as in the jupyter notebook: docs/demo.ipynb. If
the notebook fails to render on github, paste the link into nbviewer: https://nbviewer.jupyter.org.

You can find our official support forum here, under the "Matscholar" category: https://dicuss.matsci.org

## Setup

For installation and usage - it doesn't work with python3.7 as there are problems with dependencies, so use python3.6

We *highly* recommend using a [conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html) 
when working with materials scholar tools.

1. Clone or download this repo
2. Navigate to the root directory (matscholar)
3. `pip install -r requirements.txt`
4. `pip install .` [or](https://stackoverflow.com/questions/15724093/difference-between-python-setup-py-install-and-pip-install) 
`python setup.py install`


## Configuring Your API Key
The Materials Scholar API can only be accessed by providing an API key in `x-api-key` request header field. API keys are currently only available to internal collaborators at LBNL, but will be available soon. To request an API key to access the Materials Scholar API (or to request to be added to the waiting list), please contact John Dagdelen at jdagdelen@lbl.gov.

## API Usage

For convenience, the Materials Scholar API can be accessed via a python wrapper.

### Instantiating the Rester

If an API key has already been obtained, the rester is instantiated as follows:

```python
from matscholar.rest import Rester

rester = Rester(api_key="your-api-key", endpoint="https://api.matscholar.com")
```

To avoid passing the API key and endpoint as arguments, set the following environment variables 
for ease of use: `MATSCHOLAR_API_KEY`, `MATERIALS_SCHOLAR_ENDPOINT`.

### Resources

The methods of the Rester class can be used to access resources of the Materials Scholar API.

**Searching documents**

Our corpus of materials science abstracts can be searched based on text matching 
(ElasticSearch) or by filtering based on the Named Entities extracted from each document. 
Entity based searches support the following entity types: material, property, application, 
descriptor, characterization, synthesis, phase.

To get the raw text of abstracts matching a given query:

```python
# text match for "solid oxide fuel cells"
example_text = "solid oxide fuel cells"

# entity filters: include documents mentioning BaZrO3 and nanoparticles; 
# exclude documents mentioning thin films
example_entities = {"descriptor": ["nanoparticle", "-thin film"]}

docs = rester.abstracts_search(example_entities, text=example_text)
```

This will return a list of dictionaries containing the raw-text for each abstracts along with 
associated metadata.

**Searching entities**

We have extracted materials-science named entities from nearly 3.5 million materials science
absracts. Details on how this was performed can be found in Ref. [1].

The extracted named entities for each document associated with a query are returned by the 
search_ents method. This method takes as input a dictionary with entity types as keys and a list of entities
 as values. For example, to find all of the entities that co-occur with the material
"GaN":

```python
docs = rester.entities_search({"material": ["GaN"]})
```

This wil return a list of dictionaries representing documents matching the query; each dict will contain 
the DOI as well as each unique entity found in the corresponding abstract.

A summary of the entities associated with a query can be generated using the get_summary method. To get 
statistics for entities co-occuring with GaN,

```python
summary = rester.get_summary(query={"material": ["GaN"]})
```
 This will return a dictionary with entity types as keys; the values will be a list of the top entities
 that occur in documents matching the query, each item in the list will be [entity, document count, fraction].

**Named Entity Recognition**

In addition to the pre-processed entities present in our corpus, users can performed Named Entity 
Recognition on any raw materials science text. The details of the model can be found in Ref. [1].

The input should be a list of documents with the text represented as a string:

```python
doc_1 = "The bands gap of TiO2 is 3.2 eV. This was measured via photoluminescence"
doc_2 = "We deposit GaN thin films using MOCVD"
docs = [doc_1, doc_2] 
tagged_docs = rester.get_ner_tags(docs, return_type="concatenated")
```

The arguement return_type may be set to iob, concatenated, or normalized. The latter will replace
entities with their most frequently occurring synonym. A  list of tagged documents will be returned.
Each doc is a list of sentences; each sentence is a list of (word, tag) pairs.



If you use any of the API functionality in your research, please cite the following papers
where relevent:

[1] L. Weston et al., Submitted to J. Chem. Inf. Model., https://doi.org/10.26434/chemrxiv.8226068.v1

[2] V. Tshitoyan et al., Nature 571, 95 (2019).


## Contributors
@jdagdelen, @vtshitoyan, @lweston
