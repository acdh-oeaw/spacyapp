#from exceptions import ValueError, AttributeError
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import json
import spacy
from .conversion import Converter



SPACY_PIPELINE = ['tagger', 'parser', 'ner']


def check_validity_payload(kind, payload):
    if kind == "application/json+acdhlang":
        with open('jsonschema/acdh_lang_jsonschema.json') as s:
            schema = json.load(s)
            try:
                validate(payload, schema)
                return True
            except ValidationError:
                return False
    elif kind == "spacyDoc":
        if type(payload) == spacy.tokens.doc.Doc:
            return True
        else:
            return False


class PipelineProcessBase:
    accepts = ["application/json+acdhlang"]
    returns = "application/json+acdhlang"
    payload = None
    function = False
    url = False
    headers = False
    
    def convert_payload(self):


    def check_validity(self):
        if self.mime is None:
            raise ValueError('You must specify a mime type of the payload.')
        if self.payload is None:
            raise ValueError('You cant call pipeline processes without specifying a payload.')
        if self.mime not in self.accepts:
            raise ValueError('Mime type not accepted by the process.')
        if not check_validity_payload(self.mime, self.payload):
            raise ValueError('Payload is not in the correct format')

    def __init__(self, payload=None, mime=None):
        self.payload = payload
        self.mime = mime
        self.check_validity()


class SpacyProcess(PipelineProcessBase):
    accepts = ["spacyDoc", "text/plain"]
    returns = "spacyDoc"

    def process(self):
        if self.options is not None:
            if self.options['model']:
                nlp = spacy.load(self.options['model'])
            elif self.options['']
                nlp = spacy.load('de')
        if self.pipeline is None:
            disable_pipeline = [x for x in SPACY_PIPELINE]
        else:
            disable_pipeline = [
                x for x in SPACY_PIPELINE if x not in pipel
            ]
        if modell is None:
            modell = SPACY_LANG_LST[lang.lower()]
        else:
            modell = os.path.join('~/media/pipeline_models', modell)

    def __init__(self, payload=None, pipeline=None, options=None):
        super().__init__(payload=payload)
        self.pipeline = pipeline
        self.options = options
