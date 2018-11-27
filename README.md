# Materials Scholar (matscholar)

*NOTE: This library is currently being migrated from another repository and is not yet functional. Please check back later for the functional version.*

Matscholar is a library for materials-focused NLP. It is maintained by a team of researchers at UC Berkeley and Lawrence Berkeley National Laboratory as part of a project funded by the Toyota Research Institute. 

This library provides a Python interface for interacting with the Materials Scholar API, performing basic NLP tasks on scientific literature, and example notebooks on using these tools for materials discovery and design. 


## Setup

We *highly* recommend using a [conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html) when working with materials scholar tools. Below is a guide on how to set an environment variable with your api key so you don't have to supply it each time you create an instance of the Rester. 

### Configuring Your API Key
The Materials Scholar API can only be accessed by providing an API key in `x-api-key` request header field. 
To receive an API key to access the Materials Scholar API, please contact John Dagdelen at jdagdelen@lbl.gov.

Once you have an API key, you can add it as an environment variable `MATSCHOLAR_API_KEY` for ease of use. 

### Contributors
@jdagdelen, @vtshitoyan, @lweston


