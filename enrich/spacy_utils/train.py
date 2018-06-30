#
# def train(lang='de_core_news_sm', output_dir=None, n_iter=1, TRAIN_DATA=TRAIN_DATA[:4], TEST_DATA=TEST_DATA):
#     """Create a new model, set up the pipeline and train the tagger. In order to
#     train the tagger with a custom tag map, we're creating a new Language
#     instance with a custom vocab.
#     """
#     nlp = spacy.load(lang)
#     # add the tagger to the pipeline
#     # nlp.create_pipe works for built-ins that are registered with spaCy
#     tagger = nlp.get_pipe('tagger')
#     # Add the tags. This needs to be done before you start training.
# #     for tag, values in TAG_MAP.items():
# #         tagger.add_label(tag, values)
#
#     optimizer = nlp.begin_training()
#     for i in range(n_iter):
#         random.shuffle(TRAIN_DATA)
#         losses = {}
#         for text, annotations in TRAIN_DATA:
#             nlp.update([text], [{'words': annotations[0], 'tags': annotations[1]}], sgd=optimizer, losses=losses)
#         print(losses)
#
#     # test the trained model
#     test_text = TEST_DATA
#     doc = nlp(test_text)
#     print('Tags', [(t.text, t.tag_, t.pos_) for t in doc])
#
#     # save model to output directory
#     if output_dir is not None:
#         output_dir = Path(output_dir)
#         if not output_dir.exists():
#             output_dir.mkdir()
#         nlp.to_disk(output_dir)
#         print("Saved model to", output_dir)
#
#         # test the save model
#         print("Loading from", output_dir)
#         nlp2 = spacy.load(output_dir)
#         doc = nlp2(test_text)
#         print('Tags', [(t.text, t.tag_, t.pos_) for t in doc])
