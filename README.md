# nlp - An NLP-App/Service

spacyapp is a NLP service provided by [ACDH](https://acdh.oeaw.ac.at). It is built around [spaCy](https://spacy.io), but extends spacys functionalities and provides an easy to use webservice.

Our service is currently under heavy development, but it provides so far:
* RestAPI endpoints for all services
* an endpoint that provides a standard [spaCy](https://spacy.io) pipline
* an endpoint that uses [spaCy](https://spacy.io) to extract named entities
* an endpoint that returns POS tags for tokens provided
* an pipline endpoint that allows batch processing for TEI documents:
	- accepts a ZIP of TEI documents
	- uses the [xtx](https://xtx.acdh.oeaw.ac.at/index.html) tokenizer developed at [ACDH](https://acdh.oeaw.ac.at) to tokenize TEI documents while preserving existing tags
	- allows to choose between a [Treetagger based service](https://linguistictagging.eos.arz.oeaw.ac.at/) - also developed at [ACDH](https://acdh.oeaw.ac.at) - and [spaCy](https://spacy.io) for POS tagging
	- provides the processed files as TEI
	- informs users logged in via email that their job is finished (processing a lot of TEI files can take a while)

Have a look at https://spacyapp.acdh.oeaw.ac.at/ for a running version
