"""
This module provides some helper functions\
to save, clean and load spacy-like NER training data.
"""

import pandas as pd
import ast
import langid


def clean_train_data(train_data, min_ents=3, min_text_len=0, lang=['de']):

    """ removes items with no entities or fewer entities then min_ents
        :param train_data: A list of lists of spacy-like NER Tuple\
        [(('some text'), entities{[(15, 19, 'place')]}), (...)]
        :param min_ents: An integer defining the minimum amount of entities.
        :min_text_len: An integer defining the minimum length of the textself.
        :lang: A list of language codes. If populated, only samples matching those languages will\
        be included into the returned results.
        :return: A list of lists of spacy-like NER Tuple\
        [(('some text'), entities{[(15, 19, 'place')]}), (...)]
    """

    TRAIN_DATA = []
    for x in train_data:
        try:
            ents = x[1]
        except TypeError:
            ents = None
        if ents and len(ents['entities']) >= min_ents and len(x[0]) >= min_text_len:
            TRAIN_DATA.append(x)
    if len(lang) > 0:
        TRAIN_DATA_LANG = []
        for x in TRAIN_DATA:
            lng, prob = langid.classify(x[0])
            if lng in lang:
                TRAIN_DATA_LANG.append(x)
        return TRAIN_DATA_LANG

    return TRAIN_DATA


def traindata_to_csv(train_data, filename='out.csv'):

    """Saves list of lists of spacy-like NER Tuples as csv.
        :param train_data: A list of lists of spacy-like NER Tuple\
        [(('some text'), entities{[(15, 19, 'place')]}), (...)]
        :param filename: The name of the .csv file
        :returns: The filename.
    """

    df = pd.DataFrame(train_data, columns=["text", "entities"])
    df.to_csv(filename, index=False)
    return filename


def csv_to_traindata(csv):

    """ loads as csv and returns as TRAIN_DATA List
        :param csv: Path to the csv file.
        :return: A list of lists of spacy-like NER Tuple\
        [(('some text'), entities{[(15, 19, 'place')]}), (...)]
    """
    new = pd.read_csv(csv)
    TRAIN_DATA = []
    for i, row in new.iterrows():
        item = []
        item.append(row[0])
        ents = ast.literal_eval(row[1])
        item.append(ents)
        TRAIN_DATA.append(item)
    return TRAIN_DATA
