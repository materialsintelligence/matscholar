<img src="docs/matscholar_logo.png" alt="matscholar logo" width="300px">

MatScholar (Materials Scholar) is a Python library for materials-focused natural language processing (NLP). It is maintained by a team of researchers at UC Berkeley and Lawrence Berkeley National Laboratory as part of a project funded by the Toyota Research Institute.

This library provides a Python interface for interacting with the Materials Scholar API, performing basic NLP tasks on scientific text, and example notebooks on using these tools for materials discovery and design.


## Setup

We *highly* recommend using a [conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html) when working with materials scholar tools.

1. Clone or download this repo
2. Navigate to the root directory (matscholar)
3. `pip install -r requirements.txt`
4. `pip install .` [or](https://stackoverflow.com/questions/15724093/difference-between-python-setup-py-install-and-pip-install) `python setup.py install`


## Configuring Your API Key
The Materials Scholar API can only be accessed by providing an API key in `x-api-key` request header field. 
To receive an API key to access the Materials Scholar API, please contact John Dagdelen at jdagdelen@lbl.gov.

Once you have an API key, you can add it as an environment variable `MATSCHOLAR_API_KEY` for ease of use. 

## Contributors
@jdagdelen, @vtshitoyan, @lweston


