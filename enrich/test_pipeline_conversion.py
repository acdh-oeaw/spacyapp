from django.test import TestCase
import spacy
from enrich.pipeline_processes.conversion import Converter
from enrich.pipeline_processes.base import SpacyProcess
import json


class ConversionTestCase(TestCase):

    def setUp(self):
        nlp = spacy.load('de')
        txt = "Wien ist eine schöne Stadt"
        self.spacy_doc = nlp(txt)
        with open('jsonschema/acdh_json_example.json') as f:
            self.json_data = json.load(f)

#    def test_spacy_to_json(self):
#       d = Converter(data_type='spacyDoc', data=self.spacy_doc)

    def test_spacy_to_json_new(self):
        d = SpacyProcess(payload=self.json_data, mime='application/json+acdhlang')
