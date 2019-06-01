<img src="docs/matscholar_logo.png" alt="matscholar logo" width="300px">

`matscholar` (Materials Scholar) is a Python library for materials-focused natural language 
processing (NLP). It is maintained by a team of researchers at UC Berkeley and Lawrence Berkeley 
National Laboratory as part of a project funded by the Toyota Research Institute.

This library provides a Python interface for interacting with the Materials Scholar API, performing
basic NLP tasks on scientific text, and example notebooks on using these tools for materials 
discovery and design.


## Setup

We *highly* recommend using a [conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html) 
when working with materials scholar tools.

1. Clone or download this repo
2. Navigate to the root directory (matscholar)
3. `pip install -r requirements.txt`
4. `pip install .` [or](https://stackoverflow.com/questions/15724093/difference-between-python-setup-py-install-and-pip-install) 
`python setup.py install`


## Configuring Your API Key
The Materials Scholar API can only be accessed by providing an API key in `x-api-key` request header field. 
To receive an API key to access the Materials Scholar API, please contact John Dagdelen at jdagdelen@lbl.gov.

## API Usage

For convenience, the Materials Scholar API can be accessed via a python wrapper.

### Instantiating the Rester

If an API key has already been obtained, the rester is instantiated as follows:

```python
from matscholar.rest import Rester

rester = Rester(api_key="your-api-key", endpoint="api.matscholar.com")
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
example_entities = {"material": ["BaZrO3"], "descriptor": ["nanoparticle", "-thin film"]}

docs = rester.search_text_with_ents(text=example_text, filters=example_entities)
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
docs = rester.search_ents(query={"material": ["GaN"]})
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
 
To perform a fast literature review, the materials_search_ents method may be used. For a chosen application, 
this will return a list of all materials that co-occur with that application in our corpus. For example,
to see which materials co-occur with the word thermoelectric in a document,

```python
mat_list = rester.materials_search_ents(["thermoelectric"], elements=["-Pb"], cutoff=None)
```

The above search will find all materials co-occurring with thermoelectric that do not contain lead. 
The result will be a list, with each element containing a list of [material, co-occurence counts, co-occurrence dois].
 
**Word embeddings**

Materials science word embeddings trained using word2vec; details on how the embeddings were trained,
and their application in materials science discovery can be found in Ref. [2].

To get the word embedding for a given word,
```python
embedding = rester.get_embedding("photovoltaics")
```

This will return a dict containing the embedding. The word embedding will be a 200-dimensional array.

The rester also has a close_words method (based on cosine similarity of embeddings) which can be used to 
explore the semantic similarity of materials science terms; this approach can be used discover materials
for a new application (as outlined in the reference above), 

To find words with a similar embedding to photovolatic:

```python
close_words = rester.close_words("photovoltaics", top_k=1000)
```

This will return the 1000 closest words to photovoltaics. The result will be a dictionary containing 
the close words and their cosine similarity to the input word. 

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

## Citation

If you use any of the API functionality in your research, please consider citing the following papers
where relevent:

[1] Weston et al., coming soon

[2] Tshitoyan et al., Nature (accepted)


## Contributors
@jdagdelen, @vtshitoyan, @lweston
