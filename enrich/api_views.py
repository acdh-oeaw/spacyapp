import datetime
import zipfile
from os import makedirs, listdir
import shutil
import ast

import spacy
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, schema
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser
from sklearn.metrics import cohen_kappa_score, precision_recall_fscore_support
import requests
import lxml.etree as et

from enrich.spacy_utils import ner
from enrich.custom_parsers import JsonToDocParser
from enrich.custom_renderers import DocToJsonRenderer
from .tei import TeiReader
from .tasks import pipe_process_files
from django.conf import settings
from django_celery_results.models import TaskResult

nlp = spacy.load('de_core_news_sm')


@api_view(['GET', 'POST'])
@schema(None)
def nerparser(request):
    """
    get:
    Send any text as value of a *longtext* paramter

    post:
    Processes any german text which is sent as value of a *longtext* param\
    and extracts Named Entities

    """

    if request.method == 'POST':
        longtext = request.data.get('longtext')
        dont_split = request.data.get('dont_split')
    else:
        longtext = request.GET.get('longtext')
        dont_split = request.GET.get('dont_split')
    if longtext:
        doc = nlp(u"{}".format(longtext))
        enriched = ner.fetch_ner_samples(doc, dont_split=dont_split)
        return Response(enriched, content_type="application/json; charset=utf-8")
    return Response(
        {
            "Param-Name": "longtext",
            "Param-Value": "any text you want",
            "Param-Name": "dont_split",
            "Param-Value": "True",
            "POST": "json"
        }
    )


@api_view(['GET', 'POST'])
@schema(None)
def textparser(request):
    """
    get:
    Send any text as value of a *longtext* paramter

    post:
    Processes any german text which is sent as value of a *longtext* param

    """
    enriched = {}
    if request.method == 'POST':
        longtext = request.data.get('longtext')
        # print(longtext)
    else:
        longtext = request.GET.get('longtext')
    if longtext:
        doc = nlp("{}".format(longtext))
        sents = [x for x in doc.sents]
        result = []
        for x in sents:
            chunk = {}
            chunk['sent'] = "{}".format(x)
            chunk['tokens'] = []
            for y in x:
                parts = {}
                parts['text'] = y.text
                parts['lemma'] = y.lemma_
                parts['pos'] = y.pos_
                parts['tag'] = y.tag_
                parts['dep'] = y.dep_
                parts['shape'] = y.shape_
                parts['is_alpha'] = y.is_alpha
                chunk['tokens'].append(parts)
            result.append(chunk)
        enriched['result'] = result
        return Response(enriched)
    return Response(
        {
            "Param-Name": "longtext",
            "Param-Value": "any text you want",
            "POST": "json"
        }
    )


class JsonParser(APIView):
    """
    Endpoint to process text from the ACDH internal json standard

    post:
    param *tokenArray*: array of token dicts:
         param *tokenId*: Integer, token id (optional)
         param *value*: token as string
    param *options*:
          param *outputproperties*: dict.
                   e.g. {"lemma": true, "pipeline": ["tagger", "parser", "ner"]}
          param *language*: not implemented yet


    Example:
    import requests

    url = "http://127.0.0.1:8000/query/jsonparser-api/"

    payload = "
        {\"tokenArray\": [{\"value\": \"Georg\", \"whitespace\": true}, {\"value\": \"fuhr\",\
         \"whitespace\": true}, {\"value\": \"mit\", \"whitespace\": true}, {\"value\": \"dem\",\
          \"whitespace\": true}, {\"value\": \"Rad\", \"whitespace\": false}, {\"value\": \".\",\
           \"whitespace\": false}], \"language\": \"german\"}"
    headers = {
        'content-type': "application/json+acdhlang",
        'accept': "application/json+acdhlang",
        'cache-control': "no-cache",
        'postman-token': "94350f70-5d62-a4fb-ddd8-a548d6e3a528"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)
    """
    parser_classes = (JsonToDocParser,)
    renderer_classes = (DocToJsonRenderer,)

    def post(self, request, format=None):
        doc, nlp_loc, options = request.data
        for name, proc in nlp_loc.pipeline:
            doc = proc(doc)
        return Response(doc)


class NLPPipelineNew(APIView):

    parser_classes = (MultiPartParser, )
    file_types = ['application/xml+tei', 'application/json+acdhlang', 'application/xml+tcf', 'text/plain']
    zip_types = ['zip']
    
    #def process_file(self, file):

    def post(self, request, format=None):
        data = request.data
        tmp_dir = getattr(settings, "SPACYAPP_TEMP_DIR", 'tmp/')
        self.pipeline = data.get('nlp_pipeline', None)
        if self.pipeline is not None:
            self.pipeline = ast.literal_eval(self.pipeline)
        print(self.pipeline)
        file_type = data.get('file_type', None)
        self.file_type = file_type
        zip_type = data.get('zip_type', None)
        if zip_type is not None:
            if zip_type not in self.zip_types:
                raise ParseError(detail='zip type not supported')
        if file_type.lower() not in self.file_types:
            raise ParseError(detail='file type not supported')
        f = data.get('file')
        user = request.user.get_username()
        if len(user) == 0 or user is None:
            user = 'anonymous'
        fn_orig = str(f)
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        fn = '{}{}_{}'.format(tmp_dir, user, ts)
        file = '{}.{}'.format(fn, fn_orig.split('.')[1])
        with open(file, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        if request.user.is_authenticated:
            user2 = request.user.id
        else:
            user2 = None
        proc_files = pipe_process_files.delay(
            self.pipeline, file, fn, None, user, zip_type, self.file_type, user2)
        resp = {'success': True, 'proc_id': proc_files.id}
        return Response(resp)


class NLPPipeline(APIView):
    """
    Endpoint that allows to define a pipeline that should be applied to a file.

    post:
    param *file*: plain/text, raw file or list of plain/text
    param *file_type*: (string) type of file, currently only TEI,\
    acdh-json and plain-text are supported
    param *nlp_pipeline*: (list) either list of dicts with detailed settings
          for every process (not implemented yet) or list of strings.
          possible settings:
                      * acdh-tokenizer|spacy-tokenizer
                      * spacy-tagger|treetagger-tagger
                      * spacy-parser
                      * spacy-ner
    """
    parser_classes = (MultiPartParser, )
    file_types = ['tei', 'acdh-json', 'plain-text']
    zip_types = ['zip']

    def process_file(self, file):
        res = 'test'
        if self.file_type.lower() == 'tei' and self.pipeline[0].lower() == 'acdh-tokenizer':
            with open(file, 'r', encoding='utf-8') as file:
                headers = {
                    'Content-type': 'application/xml;charset=UTF-8', 'accept': 'application/xml'
                }
                url = settings.XTX_URL
                res = requests.post(url, headers=headers, data=file.read().encode('utf8'))
        if self.file_type.lower() == 'tei':
            res_tei = TeiReader(res.text)
            res = res_tei.create_tokenlist()
        if self.pipeline[1].lower() == "treetagger-tagger":
            url = settings.TREETAGGER_URL
            headers = {'accept': 'application/json'}
            payload = {'tokenArray': res, 'language': 'german',
                       "outputproperties": {"lemma": True, "no-unknown": False}}
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code != 200:
                print(res.text)
                res = res.text
            else:
                res = res.json()['tokenArray']
        spacy_pipeline = [x.split('-')[1] for x in self.pipeline if x.startswith('spacy')]
        if len(spacy_pipeline) > 0:
            headers = {'content-type': "application/json+acdhlang",
                       'accept': "application/json+acdhlang"}
            payload = {
                'tokenArray': res, 'language': 'german',
                'pipeline': spacy_pipeline
            }
            res = requests.post(
                settings.JSONPARSER_URL,
                headers=headers, json=payload
            )
            if res.status_code != 200:
                print(res.text)
                res = res.text
            else:
                res = res.json()
                res1 = [x['tokens'] for x in res['result']]
                res2 = [item for sublist in res1 for item in sublist]
        if self.file_type == 'tei':
            res = res_tei.process_tokenlist(res2)
            res = et.tostring(res, pretty_print=True)
        return res

    def post(self, request, format=None):
        data = request.data
        tmp_dir = getattr(settings, "SPACYAPP_TEMP_DIR", 'tmp/')
        self.pipeline = data.get('nlp_pipeline', None)
        if self.pipeline is not None:
            self.pipeline = ast.literal_eval(self.pipeline)
        print(self.pipeline)
        file_type = data.get('file_type', None)
        self.file_type = file_type
        zip_type = data.get('zip_type', None)
        if zip_type is not None:
            if zip_type not in self.zip_types:
                raise ParseError(detail='zip type not supported')
        if file_type.lower() not in self.file_types:
            raise ParseError(detail='file type not supported')
        f = data.get('file')
        user = request.user.get_username()
        if len(user) == 0 or user is None:
            user = 'anonymous'
        fn_orig = str(f)
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        fn = '{}{}_{}'.format(tmp_dir, user, ts)
        file = '{}.{}'.format(fn, fn_orig.split('.')[1])
        with open(file, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        if request.user.is_authenticated:
            user2 = request.user.id
        else:
            user2 = None
        proc_files = pipe_process_files.delay(
            self.pipeline, file, fn, None, user, zip_type, self.file_type, user2)
        resp = {'success': True, 'proc_id': proc_files.id}
        return Response(resp)


class TestAgreement(APIView):
    """TestAgreement: takes list of ACDH-lang formated Jsons and computes various agreement measures."""
    parser_classes = (JsonToDocParser,)

    @staticmethod
    def compute_agreement(text1, text2, agreement='cohen kappa', attribute='ENT_TYPE'):
        """compute_agreement: computes the agreement between two docs

        :param text1: spacy doc element
        :param text2: spacy doc element
        :param agreement: agreement metrics (cohen kappa or precission recall f1
        :param attribute: the attribute of the tokens to extract (e.g POS or ENT_TYPE)
        """
        attrib_parse = getattr(spacy.attrs, attribute, None)
        if attrib_parse is None:
            ParseError('{} is not a valid spacy attribute'.format(attribute))
        t1 = text1.to_array(attrib_parse)
        t2 = text2.to_array(attrib_parse)
        if agreement.lower() == 'cohen kappa':
            return {'cohen kappa': cohen_kappa_score(t1, t2)}
        elif agreement.lower() == 'precission recall f1':
            f1 = precision_recall_fscore_support(t1, t2, average='weighted')
            return {'precission': f1[0], 'recall': f1[1], 'fbeta': f1[2], 'support': f1[3]}
        else:
            ParseError('agreement metrics {} not available'.format(agreement))

    def post(self, request, format=None):
        """Post request to the API.

        :param request: DRF request object containing the request to the API
        :param format:
        """
        doc, nlp, options = request.data
        if 'agreement' not in options or 'attribute' not in options:
            ParseError('agreement or attribute parameter not specified')
        if type(doc) == list:
            if len(doc) == 2:
                res = self.compute_agreement(doc[0], doc[1],
                                             agreement=options['agreement'],
                                             attribute=options['attribute'])
                return Response(res)
            else:
                ParseError("You need to provide exactly two docs")
        else:
            ParseError("You need to provide two text docs")


@api_view()
def lemma(request):
    """
    get:
    Expects a `token` parameter (e.g. ?token=flog) which will be POS-tagged.

    """
    token = request.GET.get('token')
    enriched = {}
    if token:
        doc = nlp("{}".format(token))[0]
        enriched['token'] = token
        enriched['lemma'] = doc.lemma_
        enriched['pos'] = doc.pos_
        enriched['tag'] = doc.tag_
        return Response(enriched)
    else:
        return Response({'token': None})
