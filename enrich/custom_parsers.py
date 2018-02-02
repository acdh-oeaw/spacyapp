import spacy
from spacy.tokens import Doc, Token
from rest_framework.parsers import JSONParser

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
