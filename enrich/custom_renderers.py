from rest_framework import renderers
from enrich.spacy_utils.ner import format_iob_tag


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
            if y.has_extension('tokenId'):
                parts['tokenId'] = y._.tokenId
            else:
                parts['tokenId'] = y.i
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
