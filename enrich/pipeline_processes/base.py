#from exceptions import ValueError, AttributeError
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import json


def check_validity_payload(kind, payload):
    if kind == "application/json+acdhlang":
        with open('jsonschema/acdh_lang_jsonschema.json') as s:
            schema = json.load(s)
            try:
                validate(payload, schema)
                return True
            except ValidationError:
                return False
    else:
        return True


class PipelineProcessBase:
    accepts = "application/json+acdhlang"
    returns = "application/json+acdhlang"
    payload = None
    function = False
    url = False
    headers = False

    def check_validity(self):
        if self.payload is None:
            raise ValueError('You cant call pipeline processes without specifying a payload.')
        if not check_validity_payload(self.accepts, self.payload):
            raise ValueError('Payload is not in the correct format')

    def __init__(self, payload=None):
        self.payload = payload
        self.check_validity()


class SpacyProcess(PipelineProcessBase):
    accepts = "spacyDoc"
    returns = "spacyDoc"

    def process(self):
        pass

    def __init__(self, payload=None, pipeline=None):
        if pipeline is None:
            raise ValueError('Pipeline needs to be defined in spacy process.')
        super().__init__(payload=payload)

