import spacy
from rest_framework.response import Response
from rest_framework.decorators import api_view, schema
from rest_framework.views import APIView
from enrich.custom_parsers import JsonToDocParser
from enrich.custom_renderers import DocToJsonRenderer
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import ParseError

import datetime
import zipfile
from os import makedirs, listdir

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
          param *outputproperties*: dict of parts of the pipeline to use.
                   e.g. {"lemma": true, "ner": false, "tagger": true}
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
        return file
    
    def post(self, request, format=None):
        data = request.data
        self.pipeline = request.data.get('NLPPipeline', None)
        file_type = request.data.get('fileType', None)
        zip_type = request.data.get('zipType', None)
        if zip_type is not None:
            if zip_type not in self.zip_types:
                raise ParseError(detail='zip type not supported')
        if file_type.lower() not in self.file_types:
            raise ParseError(detail='file type not supported')
        f = data.get('file')
        print(type(f))
        fn_orig = str(f)
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        user = request.user.get_username()
        if len(user) == 0 or user is None:
            user = 'anonymous'
        fn = 'tmp/{}_{}'.format(user, ts)
        with open('{}.{}'.format(fn, fn_orig.split('.')[1]), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        if zip_type is not None:
            makedirs('tmp/{}_{}_folder'.format(user, ts))
            makedirs('tmp/{}_{}_output'.format(user, ts))
            zip_ref = zipfile.ZipFile('tmp/{}_{}.{}'.format(user, ts, fn_orig.split('.')[1]), 'r')
            zip_ref.extractall('tmp/{}_{}_folder'.format(user, ts))
            zip_ref.close()
            for filename in listdir('tmp/{}_{}_folder'.format(user, ts)):
                res = self.process_file(open(filename, 'rb'))
                with open('tmp/{}_{}_output/{}'.format(user, ts, filename), 'wb+') as out:
                    out.write(res)
            zipf = zipfile.ZipFile('{}_output.zip'.format(fn), 'w', zipfile.ZIP_DEFLATED)
            for filename in listdir('tmp/{}_{}_output'.format(user, ts)):
                zipf.write('tmp/{}_{}_output/{}'.format(user, ts, filename))
            zipf.close()
            
        return Response(data)

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
