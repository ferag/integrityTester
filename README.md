Integrity Tester
-----------------------------------
This script is a prototype to measure Datasets and metadata stored in a repository like Zenodo.

The script loads config.py to get the following information:

 - ACCESS_TOKEN: Token to communicate with repository API.
 - API_URL: API endpoint for repository.
 - OAI-PMH: OAI-PMH protocol endpoint (from repository, if it is compatible).
 - OAI-PMH-ID-FORM : format defined to manage the object identifier via OAI-PMH.
 
 Prototype
 -----------------------------------
 The script is a proof-of-concept and it proves that it can potentially be applied combining datasets and metadata standards like EML. It also exploit REST APIs from repositories and OAI-PMH protocol
