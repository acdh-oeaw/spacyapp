from rest_framework import renderers
from spacytei.ner import format_iob_tag


def doc_to_tokenlist_no_sents(doc):
    result = []
    for x in doc:
        token = {}
        token['tokenId'] = x._.tokenId
        token['value'] = x.text
        token['lemma'] = x.lemma_
        token['pos'] = x.pos_
        token['type'] = x.tag_
        token['dep'] = x.dep_
        token['shape'] = x.shape_
        token['is_alpha'] = x.is_alpha
        token['ent_iob'] = x.ent_iob_
        token['iob'] = format_iob_tag(x)
        token['ent_type'] = x.ent_type_
        result.append(token)
    return result


def doc_to_tokenlist(doc):
    sents = [x for x in doc.sents]
    result = []
    counter = 0
    for x in sents:
        chunk = {}
        chunk['sent'] = "{}".format(x)
        chunk['tokens'] = []
        for y in x:
            parts = {}
            parts['tokenId'] = y._.tokenId
            parts['value'] = y.text
            parts['lemma'] = y.lemma_
            parts['pos'] = y.pos_
            parts['type'] = y.tag_
            parts['dep'] = y.dep_
            parts['shape'] = y.shape_
            parts['is_alpha'] = y.is_alpha
            parts['ent_iob'] = y.ent_iob_
            parts['iob'] = format_iob_tag(y)
            parts['ent_type'] = y.ent_type_
            chunk['tokens'].append(parts)
            counter += 1
        result.append(chunk)
    return result


class DocToJsonRenderer(renderers.JSONRenderer):
    media_type = "application/json+acdhlang"

    def render(self, data, media_type=None, renderer_context=None):
        result = doc_to_tokenlist(data)
        enriched = {}
        # sents = [x for x in data.sents]
        # result = []
        # counter = 0
        # for x in sents:
        #     chunk = {}
        #     chunk['sent'] = "{}".format(x)
        #     chunk['tokens'] = []
        #     for y in x:
        #         parts = {}
        #         parts['tokenId'] = y._.tokenId
        #         parts['value'] = y.text
        #         parts['lemma'] = y.lemma_
        #         parts['pos'] = y.pos_
        #         parts['type'] = y.tag_
        #         parts['dep'] = y.dep_
        #         parts['shape'] = y.shape_
        #         parts['is_alpha'] = y.is_alpha
        #         parts['ent_iob'] = y.ent_iob_
        #         parts['ent_type'] = y.ent_type_
        #         chunk['tokens'].append(parts)
        #         counter += 1
        #     result.append(chunk)
        enriched['result'] = result
        res = super(DocToJsonRenderer, self).render(enriched, "application/json", renderer_context)
        return res
