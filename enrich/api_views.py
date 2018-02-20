import spacy
from rest_framework.response import Response
from rest_framework.decorators import api_view, schema
from rest_framework.views import APIView
from enrich.custom_parsers import JsonToDocParser
from enrich.custom_renderers import DocToJsonRenderer
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import ParseError
from .tei import TeiReader

import datetime
import zipfile
from os import makedirs, listdir
import requests
import shutil
import lxml.etree as et
import json

nlp = spacy.load('de_core_news_sm')


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
        longtext = request.POST.get('longtext')
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
            "POST": "form-data or x-www-form-urlencoded"
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


class NLPPipeline(APIView):
    """
    Endpoint that allows to define a pipeline that should be applied to a file.
 
    post:
    param *file*: plain/text, raw file or list of plain/text
    param *fileType*: (string) type of file, currently only TEI, acdh-json and plain-text are supported
    param *NLPPipeline*: (list) either list of dicts with detailed settings
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
                headers = {'Content-type': 'application/xml;charset=UTF-8', 'accept': 'application/xml'}
                url = 'https://tokenizer.eos.arz.oeaw.ac.at/exist/restxq/xtoks/tokenize/default'
                res = requests.post(url, headers=headers, data=file.read().encode('utf8'))
        if self.file_type.lower() == 'tei':
            res_tei = TeiReader(res.text)
            res = res_tei.create_tokenlist()
        if self.pipeline[1].lower() == "treetagger-tagger":
            url = "https://linguistictagging.eos.arz.oeaw.ac.at"
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
            payload = {'tokenArray': res, 'language': 'german', 'options': {'outputproperties': {'pipeline': spacy_pipeline}}}
            res = requests.post("https://spacyapp.eos.arz.oeaw.ac.at/query/jsonparser-api/", headers=headers, json=payload)
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
        tmp_dir = 'tmp/'
        dwld_dir = 'download/'
        data = request.data
        print(data)
        self.pipeline = data.get('NLPPipeline', None)
        if self.pipeline is not None:
            self.pipeline = self.pipeline.split(',')
        file_type = data.get('fileType', None)
        self.file_type = file_type
        zip_type = data.get('zipType', None)
        print(zip_type)
        if zip_type is not None:
            if zip_type not in self.zip_types:
                raise ParseError(detail='zip type not supported')
        if file_type.lower() not in self.file_types:
            raise ParseError(detail='file type not supported')
        f = data.get('file')
        print(f)
        fn_orig = str(f)
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        user = request.user.get_username()
        if len(user) == 0 or user is None:
            user = 'anonymous'
        fn = '{}{}_{}'.format(tmp_dir, user, ts)
        with open('{}.{}'.format(fn, fn_orig.split('.')[1]), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        if zip_type is not None:
            makedirs('{}{}_{}_folder'.format(tmp_dir, user, ts))
            makedirs('{}{}_{}_output'.format(tmp_dir, user, ts))
            zip_ref = zipfile.ZipFile('{}{}_{}.{}'.format(tmp_dir, user, ts, fn_orig.split('.')[1]), 'r')
            zip_ref.extractall('{}{}_{}_folder'.format(tmp_dir, user, ts))
            zip_ref.close()
            for filename in listdir('{}{}_{}_folder'.format(tmp_dir, user, ts)):
                res = self.process_file('{}{}_{}_folder/{}'.format(tmp_dir, user, ts, filename))
                with open('{}{}_{}_output/{}'.format(tmp_dir, user, ts, filename), 'wb') as out:
                    #out.write(res.text)
                    out.write(res)
            zipf = zipfile.ZipFile('{}_output.zip'.format(fn), 'w', zipfile.ZIP_DEFLATED)
            for filename in listdir('{}{}_{}_output'.format(tmp_dir, user, ts)):
                zipf.write('{}{}_{}_output/{}'.format(tmp_dir, user, ts, filename))
            zipf.close()
            shutil.copy('{}_output.zip'.format(fn), '{}{}_output.zip'.format(dwld_dir, fn.split('/')[1]))
            resp = {'status': 'finished', 'download': '{}{}_output.zip'.format(dwld_dir, fn.split('/')[1])}
            return Response(resp)


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
