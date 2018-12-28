"""
This module provides some helper functions\
to save, clean and load spacy-like NER training data.
"""

import pandas as pd
import ast


def clean_train_data(train_data, min_ents=3):

    """ removes items with no entities or fewer entities then min_ents
        :param train_data: A list of lists of spacy-like NER Tuple\
        [(('some text'), entities{[(15, 19, 'place')]}), (...)]
        :param min_ents: An integer defining the minimum amount of entities.
        :return: A list of lists of spacy-like NER Tuple\
        [(('some text'), entities{[(15, 19, 'place')]}), (...)]
    """

    TRAIN_DATA = []
    for x in train_data:
        try:
            ents = x[1]
        except TypeError:
            ents = None
        if ents and len(ents['entities']) > min_ents:
            TRAIN_DATA.append(x)
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
