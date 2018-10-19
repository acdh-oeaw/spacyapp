import json

import spacy
from django.test import TestCase

from enrich.pipeline_processes.base import SpacyProcess
from enrich.pipeline_processes.conversion import Converter


class ConversionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        nlp = spacy.load("de")
        cls.txt = "Wien ist eine schöne Stadt"
        cls.spacy_doc = nlp(cls.txt)
        with open("jsonschema/acdh_json_example.json") as f:
            cls.json_data = json.load(f)

    def test_json_to_spacy(self):
        d = SpacyProcess(payload=self.json_data, mime="application/json+acdhlang")
        res = d.process()
        print([x for x in res.ents])
        ents = [str(x) for x in res.ents]
        self.assertIn("Wien", ents)

    def test_plaintext_to_spacy(self):
        d = SpacyProcess(payload=self.txt, mime="text/plain")
        res = d.process()
        print([x for x in res.ents])
        ents = [str(x) for x in res.ents]
        self.assertIn("Wien", ents)

    def test_json_to_spacy_without_ner(self):
        d = SpacyProcess(
            payload=self.json_data,
            mime="application/json+acdhlang",
            pipeline=["tagger", "parser"],
        )
        res = d.process()
        print([x for x in res.ents])
        ents = [str(x) for x in res.ents]
        self.assertNotIn("Wien", ents)
