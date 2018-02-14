import spacy
from spacy.tokens import Doc, Token
from rest_framework.parsers import JSONParser, BaseParser
from rest_framework.exceptions import ParseError

from django.http.multipartparser import \
    MultiPartParser as DjangoMultiPartParser

from django.http.multipartparser import (
    ChunkIter, MultiPartParserError, parse_header
)
from django.utils import six
from django.conf import settings

spacy_lang_lst = {"german": "de_core_news_sm",
                  "de": "de_core_news_sm",
                  "deutsch": "de_core_news_sm",
                  "ger": "de_core_news_sm"}


class JsonToDocParser(JSONParser):
    """Parser parsing a Json into a spacy Doc element"""

    media_type = "application/json+acdhlang"

    def parse(self, stream, media_type=None, parser_context=None):
        json = super(JsonToDocParser, self).parse(stream, "application/json", parser_context)
        lang = json.get("language", "german")
        Token.set_extension('tokenId', False)
        nlp = spacy.load(spacy_lang_lst[lang.lower()])
        ar_tok = [x['value'] for x in json['tokenArray']]
        ar_wsp = [x.get('whitespace', True) for x in json['tokenArray']]
        doc = Doc(nlp.vocab, words=ar_tok, spaces=ar_wsp)
        for id, t in enumerate(doc):
            t._.set('tokenId', json['tokenArray'][id].get('tokenId', False))

        return doc, nlp, json.pop('tokenArray', None)


class DataAndFiles(object):
    def __init__(self, data, files):
        self.data = data
        self.files = files


class MultiPartParser(BaseParser):
    """
    Parser for multipart form data, which may include file data.
    """
    media_type = 'multipart/form-data'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as a multipart encoded form,
        and returns a DataAndFiles object.
        `.data` will be a `QueryDict` containing all the form parameters.
        `.files` will be a `QueryDict` containing all the form files.
        """
        parser_context = parser_context or {}
        request = parser_context['request']
        encoding = parser_context.get('encoding', 'utf8')
        meta = request.META.copy()
        meta['CONTENT_TYPE'] = media_type
        upload_handlers = request.upload_handlers
        print(request)

        try:
            parser = DjangoMultiPartParser(meta, stream, upload_handlers, encoding)
            data, files = parser.parse()
            print('try worked')
            return DataAndFiles(data, files)
        except Exception as exc:
            print('exception {}'.format(six.text_type(exc)))
            raise ParseError('Multipart form parse error - %s' % six.text_type(exc))


class NLPPipelineParser(MultiPartParser):
    """
    Parser parsing the ACDH internal NLP pipeline format
    """

    media_type = "multipart/form-data+acdhlangpipline"
    file_types = ['TEI', 'acdh-json', 'plain-text']

    def parse(self, stream, media_type=None, parser_context=None):
        print('parsing started')
        data2 = super(NLPPipelineParser, self).parse(stream, "multipart/form-data", parser_context)
        print('parser finished')
        print(data2)
        if data2['fileType'] not in self.file_types:
            raise ParseError(info='unsopported file-type set')

        return data
