#from exceptions import ValueError, AttributeError
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import json
import spacy
from .conversion import Converter
from enrich.custom_parsers import SPACY_LANG_LST, SPACY_PIPELINE



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
    """PipelineProcessBase: Baseclass for deriving NLP processes"""
    accepts = ["application/json+acdhlang"]
    returns = "application/json+acdhlang"
    payload = None
    function = False
    url = False
    headers = False
    valid = False
    
    def convert_payload(self):
        self.payload = Converter(data_type=self.mime, data=self.payload, original_process=self).convert(to=self.accepts[0])
        print('payload converted: {}'.format(self.payload))
        self.mime = self.accepts[0]
        self.check_validity()

    def check_validity(self):
        """check_validity: checks if the payload is accepted by the function.
           Starts vonvering process if needed.
        """
        if self.mime is None:
            raise ValueError('You must specify a mime type of the payload.')
        if self.payload is None:
            raise ValueError('You cant call pipeline processes without specifying a payload.')
        if not check_validity_payload(self.mime, self.payload):
            raise ValueError('Payload is not in the correct format')
        if self.mime not in self.accepts:
            self.convert_payload()
        self.valid = True

    def __init__(self, **kwargs):
        """__init__

        :param payload: data for the process
        :param mime: mime type of the payload data
        """
        self.payload = kwargs.get('payload', None)
        self.mime = kwargs.get('mime', None)
        print('payload: {}'.format(self.payload))
        self.check_validity()


class SpacyProcess(PipelineProcessBase):
    accepts = ["spacyDoc", "text/plain"]
    returns = "spacyDoc"

    def process(self):
       pass 

    def __init__(self, options=None, pipeline=None, **kwargs):
        self.pipeline = pipeline
        self.options = options
        if self.options is not None:
            if self.options['model']:
                model = os.path.join('~/media/pipeline_models', self.options['model']) 
            elif self.options['language']:
                model = SPACY_LANG_LST[self.options['language'].lower()]
        else:
            model = 'de'
        if self.pipeline is None:
            disable_pipeline = []
        else:
            disable_pipeline = [
                x for x in SPACY_PIPELINE if x not in self.pipeline
            ]
        self.nlp = spacy.load(
            model,
            disable=disable_pipeline,
        )
        super().__init__(**kwargs)
        if not self.valid:
            raise ValueError('Something went wrong in the data conversion. Data is not valid.')
