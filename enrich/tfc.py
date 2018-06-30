from enrich.tei import XMLReader


class Tcf(XMLReader):

    """ a class to read an process tfc-documents
    tried with 'data/nn_nrhz_001_1418.tcf.xml'

    """

    def list_nodes(self, element):
        """ returns a list of passed in element-nodes"""
        expr = "//tcf:*[local-name() = $name]"
        nodes = self.tree.xpath(expr, name=element, namespaces=self.nsmap)
        return nodes

    def list_multiple_nodes(self, elements=['token', 'lemma', 'tag', 'sentence']):
        """ returns a dict with keys of past in elements and a list of those nodes as values"""
        expr = "//tcf:*[local-name() = $name]"
        nodes = {}
        for x in elements:
            nodes[x] = self.list_nodes(x)
        return nodes

    def count_multiple_nodes(self, elements=['token', 'lemma', 'tag', 'sentence']):
        """ counts the number of nodes of the passed in elements """
        nodes = self.list_multiple_nodes(elements)
        result = {}
        for key, value in nodes.items():
            result[key] = len(value)
        return result

    def create_sent_list(self):
        """ create a list of dicts for each sentence with their according token elements"""
        elements = ['token', 'lemma', 'tag', 'sentence']
        start = 0
        end = 0
        sent_list = []
        nodes = self.list_multiple_nodes(elements)
        sentences = nodes['sentence']
        tokens = nodes['token']
        tags = nodes['tag']
        lemmas = nodes['lemma']
        for x in sentences:
            sent = {}
            token_count = len(x.xpath('./@tokenIDs')[0].split(' '))
            end = start + token_count
            sent['sent_id'] = x.xpath('./@ID')[0]
            sent['words'] = tokens[start:end]
            sent['tags'] = tags[start:end]
            sent['lemmas'] = lemmas[start:end]
            start = end
            sent_list.append(sent)
        return sent_list

    def tag_train_data(self):
        """ returns a list of samples to trains spacy's pos-tagger"""
        TRAIN_DATA = []
        for x in self.create_sent_list():
            text = (" ".join([y.text for y in x['words']]))
            tags = {'tags': [y.text for y in x['tags']]}
            words = {'word': [y.text for y in x['words']]}
            lemmas = {'lemma': [y.text for y in x['lemmas']]}
            TRAIN_DATA.append((text, [words, tags, lemmas]))
        return TRAIN_DATA

    def create_tokenlist(self):
        """ returns a list of token-dicts extracted from tcf:token """
        words = self.list_nodes('token')
        token_list = []
        for x in words:
            token = {}
            token['value'] = x.text
            token['tokenId'] = x.xpath('./@ID')[0]
            try:
                follows = x.getnext().text
            except AttributeError:
                follows = None
            if follows:
                if follows[0].isalnum():
                    token['whitespace'] = True
                elif follows[0] == "„":
                    token['whitespace'] = True
                elif follows[0] == "(":
                    token['whitespace'] = True
                else:
                    token['whitespace'] = False
            else:
                token['whitespace'] = False
            token_list.append(token)
        return token_list
