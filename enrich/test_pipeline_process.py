from django.test import TestCase
import json
from enrich.pipeline_processes import base


class PipelineBaseTestCase(TestCase):
    def setUp(self):
        with open('jsonschema/acdh_json_example.json') as f:
            self.json_data = json.load(f)

    def test_validity_json(self):
        base.PipelineProcessBase(payload=self.json_data)

    def test_validity_json_false(self):
        'This test is expected to fail'
        json_neu = self.json_data
        json_neu['dasd'] = 10
        #json_neu['tokenArray'][0]['tokenId'] = 'hhhs'
        base.PipelineProcessBase(payload=json_neu)

