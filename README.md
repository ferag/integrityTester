Integrity Tester
-----------------------------------
This script is a prototype to measure Datasets and metadata stored in a repository like Zenodo.

The script loads config.py to get the following information:

 - ACCESS_TOKEN: Token to communicate with repository API.
 - ONEDATA:ACCESS_TOKEN: Onedata Token to communicate with onedata API.
 - ONEDATA_API_URL: Endpoint for onedata cdmi API.
 - API_URL: API endpoint for repository.
 - OAI-PMH: OAI-PMH protocol endpoint (from repository, if it is compatible).
 - OAI-PMH-ID-FORM : format defined to manage the object identifier via OAI-PMH.
 
 Prototype
 -----------------------------------
 The script is a proof-of-concept and it proves that it can potentially be applied combining datasets and metadata standards like EML. It also exploit REST APIs from repositories and OAI-PMH protocol.
 
 It includes two different versions:
  - integrityTester_zenodo.py: Provides an example about how to measure data FAIRness in Zenodo. By default, it cheks an example dataset
  - interityTester_onedata.py: Provides an example about how to measure data FAIRness with onedata. It requires to be registered in onedata "onezone".
