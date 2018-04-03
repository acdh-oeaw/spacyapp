import spacy

nlp = spacy.load('de_core_news_sm')


def fetch_ner_samples(spacydoc):
    sents = [x for x in spacydoc.sents]
    ent_per_sent = []
    doc = None
    for sent in sents:
        doc = nlp(sent.text)
        for ent in doc.ents:
            sample = {}
            sample['sent'] = sent.text
            sample['ent'] = ent.text
            sample['start_char'] = ent.start_char
            sample['end_char'] = ent.end_char
            sample['label'] = ent.label_
            sample['markup'] = sent.text.replace(ent.text, "{}"+ent.text+"{}")
            dict_string = "|".join([
                sent.text, ent.text, ent.label_,
                "{}".format(ent.start_char), "{}".format(ent.end_char)
            ])
            hash_id = hash(dict_string)
            sample['hash_id'] = hash_id
            ent_per_sent.append(sample)
    return ent_per_sent
