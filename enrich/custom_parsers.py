import jmespath
import spacy
from rest_framework.parsers import JSONParser
from spacy.tokens import Doc, Token

spacy_lang_lst = {
    "german": "de_core_news_sm",
    "de": "de_core_news_sm",
    "deutsch": "de_core_news_sm",
    "ger": "de_core_news_sm"
}

spacy_pipeline = ['tagger', 'parser', 'ner']

SPACY_ACCEPTED_DATA = ['POS', 'ENT_TYPE']


def process_tokenlist(nlp, tokenlist, enriched=False):
    """process_tokenlist: creates a spacy doc element of a token list

    :param nlp: spacy NLP element
    :param tokenlist: list of dicts containing tokens and parameters
    :param enriched: if set to True spacy pipeline is run
    """
    json = {}
    json['tokenArray'] = tokenlist
    ar_tok = [x['value'] for x in json['tokenArray']]
    ar_wsp = [x.get('whitespace', True) for x in json['tokenArray']]
    if Token.get_extension('tokenId') is None:
        Token.set_extension('tokenId', default=False)
    doc = Doc(nlp.vocab, words=ar_tok, spaces=ar_wsp)
    for id, t in enumerate(doc):
        t._.set('tokenId', json['tokenArray'][id].get('tokenId', False))
        t_type = json['tokenArray'][id].get('type', False)
        if not t.tag_ and t_type:
            t.tag_ = t_type
        for k in json['tokenArray'][id].keys():
            if k.upper() in SPACY_ACCEPTED_DATA:
                setattr(t, k.lower(), json['tokenArray'][id][k])  # TODO: need to set ent_iob
    if enriched:
        for name, proc in nlp.pipeline:
            doc = proc(doc)
    return doc


class JsonToDocParser(JSONParser):
    """Parser parsing a Json into a spacy Doc element
    Takes either a list of tokenArrays or one tokenArray, a language and a options parameter.
    Returns either a list of docs or a single doc, a nlp element and the options
    """

    media_type = "application/json+acdhlang"

    def parse(self, stream, media_type=None, parser_context=None):
        json = super(
            JsonToDocParser,
            self,
        ).parse(
            stream,
            "application/json",
            parser_context,
        )
        lang = json.get("language", "german")
        options = json.get("options", False)
        disable_pipeline = []
        if options:
            pipel = jmespath.search('outputproperties.pipeline', options)
            if pipel is None:
                disable_pipeline = [x for x in spacy_pipeline]
            else:
                disable_pipeline = [x for x in spacy_pipeline if x not in pipel]
        nlp = spacy.load(
            spacy_lang_lst[lang.lower()],
            disable=disable_pipeline,
        )
        token_array = json.get('tokenArray', None)
        if token_array is None:
            doc_list = json.get('docList', None)
            if doc_list is not None:
                doc = []
                for token_array in doc_list:
                    doc2 = process_tokenlist(nlp, token_array)
                    doc.append(doc2)
            else:
                return None
        else:
            doc = process_tokenlist(nlp, json['tokenArray'])

        return doc, nlp, options
