from rest_framework import renderers


class DocToJsonRenderer(renderers.JSONRenderer):
    media_type = "application/json+acdhlang"

    def render(self, data, media_type=None, renderer_context=None):
        enriched = {}
        sents = [x for x in data.sents]
        result = []
        counter = 0
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
                parts['token_id'] = counter
                chunk['tokens'].append(parts)
                counter += 1
            result.append(chunk)
        enriched['result'] = result
        res = super(DocToJsonRenderer, self).render(enriched, "application/json", renderer_context)
        return res
