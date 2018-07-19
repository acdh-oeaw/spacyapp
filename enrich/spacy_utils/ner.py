import spacy

nlp = spacy.load('de_core_news_sm')


def format_iob_tag(token):
    if token.ent_iob_ != 'O':
        iob_tag = "{0}-{1}".format(token.ent_iob_, token.ent_type_)
    else:
        iob_tag = token.ent_iob_
    return iob_tag


def fetch_ner_samples(spacydoc):
    """ takes a doc object and genereates NER-Training samples """
    spacy_samples = []
    sents = [x for x in spacydoc.sents]
    doc = None
    for sent in sents:
        doc = nlp(sent.text)
        spacy_sample = (sent.text, {'entities': []})
        for ent in doc.ents:
            spacy_sample[1]['entities'].append((ent.start_char, ent.end_char, ent.label_))
        spacy_samples.append(spacy_sample)
    return spacy_samples
