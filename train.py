from __future__ import unicode_literals, print_function

import datetime
import glob
import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
from spacytei.data_prep import csv_to_traindata, clean_train_data


"""Example of training spaCy's named entity recognizer, starting off with an
existing model or a blank model.

For more details, see the documentation:
* Training: https://spacy.io/usage/training
* NER: https://spacy.io/usage/linguistic-features#named-entities

Compatible with: spaCy v2.0.0+
"""


# @plac.annotations(
#     model=("Model name. Defaults to blank 'de_core_news_sm' model.", "option", "m", str),
#     output_dir=("Optional output directory", "option", "o", Path),
#     n_iter=("Number of training iterations", "option", "n", int),
# )
def main(
    model=None,
    output_dir="data/gesamtakademie_custom_v_5500_35",
    n_iter=35,
    train_data="data/gesamtakademie_p_sents_all.csv",
    n_samples=5500,
    new_label=None
):
    """Load the model, set up the pipeline and train the entity recognizer."""

    abs_start_time = datetime.datetime.now()

    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.load(r'C:\Users\pandorfer\Documents\Redmine\prodigy\work\akademie\akademie_custom_vector')  # create blank Language class
        print("Created blank model")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")

    if new_label:
        if model is None:
            optimizer = nlp.begin_training()
        else:
            optimizer = nlp.entity.create_optimizer()
        ner.add_label(new_label)

    TRAIN_DATA = csv_to_traindata(train_data)[:n_samples]
    # TRAIN_DATA = clean_train_data(TRAIN_DATA, min_ents=2, min_text_len=5)
    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):  # only train NER
        # reset and initialize the weights randomly – but only if we're
        # training a new model
        if model is None:
            nlp.begin_training()
        for itn in range(n_iter):
            print("Iteration Number: {}".format(itn))
            start_time = datetime.datetime.now()
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 16.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                if new_label:
                    try:
                        nlp.update(
                            texts,
                            annotations,
                            sgd=optimizer,
                            drop=0.35,
                            losses=losses
                        )
                    except Exception as e:
                        print(annotations)
                else:
                    try:
                        nlp.update(
                            texts,  # batch of texts
                            annotations,  # batch of annotations
                            drop=0.5,  # dropout - make it harder to memorise data
                            losses=losses,
                        )
                    except Exception as e:
                        print(annotations)
            print("Losses", losses)
            end_time = datetime.datetime.now()
            print("Duration: {}".format(end_time - start_time))
            print("######################")

    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)
    abs_end_time = datetime.datetime.now()
    overall_duration = print(str(abs_end_time - abs_start_time))


if __name__ == "__main__":
    plac.call(main)
