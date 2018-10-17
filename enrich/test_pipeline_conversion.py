from django.test import TestCase
import spacy
from enrich.pipeline_processes.conversion import Converter


class ConversionTestCase(TestCase):

    def setUp(self):
        nlp = spacy.load('de')
        txt = "Wien ist eine schöne Stadt"
        self.spacy_doc = nlp(txt)

    def test_spacy_to_json(self):
        d = Converter(data_type='spacyDoc', data=self.spacy_doc)
