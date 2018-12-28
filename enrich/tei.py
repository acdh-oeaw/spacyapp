import lxml.etree as ET
import time
import datetime
import re

NER_TAG_MAP = {
    "persName": "PER",
    "person": "PER",
    "placeName": "LOC",
    "place": "LOC",
    "orgName": "ORG",
    "org": "ORG",
    "work": "MISC",
    "workName": "MISC"
}

ns_tei = {'tei': "http://www.tei-c.org/ns/1.0"}
ns_xml = {'xml': "http://www.w3.org/XML/1998/namespace"}


class XMLReader():

    """ a class to read an process tei-documents"""

    def __init__(self, xml):
        self.ns_tei = {'tei': "http://www.tei-c.org/ns/1.0"}
        self.ns_xml = {'xml': "http://www.w3.org/XML/1998/namespace"}
        self.ns_tcf = {'tcf': "http://www.dspin.de/data/textcorpus"}
        self.nsmap = {
            'tei': "http://www.tei-c.org/ns/1.0",
            'xml': "http://www.w3.org/XML/1998/namespace",
            'tcf': "http://www.dspin.de/data/textcorpus"
        }
        self.file = xml
        try:
            self.original = ET.parse(self.file)
        except:
            self.original = ET.fromstring(self.file)
        try:
            self.tree = ET.parse(self.file)
        except:
            self.tree = ET.fromstring(self.file)
        try:
            self.parsed_file = ET.tostring(self.tree, encoding="utf-8")
        except:
            self.parsed_file = "parsing didn't work"

    def tree_to_file(self, file=None):
        """saves current tree to file"""
        import lxml.etree as ET
        if file:
            pass
        else:
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
            file = "{}.xml".format(timestamp)

        with open(file, 'wb') as f:
            f.write(ET.tostring(self.tree))
        return file


class TeiReader(XMLReader):

    """ a class to read an process tei-documents"""

    def extract_ne_elements(self, ne_xpath='.//tei:body//tei:rs'):

        """ extract elements tagged as named entities
        :param ne_xpath: An XPath expression pointing to elements used to tagged NEs.
        :return: A list of elements

        """

        ne_elements = self.tree.xpath(ne_xpath, namespaces=self.ns_tei)
        return ne_elements

    def extract_ne_dicts(self, ne_xpath='.//tei:body//tei:rs'):

        """ extract strings tagged as named entities
        :param ne_xpath: An XPath expression pointing to elements used to tagged NEs.
        :return: A list of NE-dicts containing the 'text' and the 'ne_type'
        """

        ne_elements = self.extract_ne_elements(ne_xpath)
        ne_dicts = []
        for x in ne_elements:
            item = {}
            item['text'] = re.sub('\s+', ' ', x.text).strip()
            try:
                ne_type = NER_TAG_MAP.get("{}".format(x.xpath('./@type')[0], 'MISC'))
            except (IndexError, KeyError) as e:
                ne_type = None
            if ne_type is not None:
                item['ne_type'] = ne_type
            else:
                ne_type = NER_TAG_MAP.get("{}".format(x.xpath("name()"), 'MISC'))
                item['ne_type'] = ne_type
            ne_dicts.append(item)

        return ne_dicts

    def create_plain_text(self, start_node='tei:body', ne_xpath='.//tei:body//tei:rs'):

        """ extracts all text nodes from given element
        :param start_node: An XPath expressione pointing to\
        an element which text nodes should be extracted
        :return: A normalized, cleaned plain text
        """
        try:
            result = self.tree.xpath(start_node, namespaces=self.ns_tei)[0]
        except IndexError:
            print("start_node: {} couldn't be found".format(start_node))
            result = []
        if result is not None:
            result = re.sub('\s+', ' ', "".join(result.xpath(".//text()"))).strip()

        return result

    def extract_ne_offsets(self, start_node='.//tei:body', ne_xpath='.//tei:body//tei:rs'):

        """ extracts offsets of NEs and the NE-type
        :param start_node: An XPath expressione pointing to\
        an element which text nodes should be extracted
        :param ne_xpath: An XPath expression pointing to elements used to tagged NEs.
        :return: A list of spacy-like NER Tuples [('some text'), entities{[(15, 19, 'place')]}]
        """

        plain_text = self.create_plain_text(start_node)
        ner_dicts = self.extract_ne_dicts(ne_xpath)
        if len(ner_dicts) == 0:
            return None
        else:
            entities = []
            for x in ner_dicts:
                if x['text'] != "":
                    for m in re.finditer(x['text'], plain_text):
                        entities.append([m.start(), m.end(), x['ne_type']])
            entities = [item for item in set(tuple(row) for row in entities)]
            entities = sorted(entities, key=lambda x: x[0])
            ents = []
            next_item_index = 1
            # remove entities with the same start offset
            for x in entities:
                cur_start = x[0]
                try:
                    next_start = entities[next_item_index][0]
                except IndexError:
                    next_start = 9999999999999999999999
                if cur_start == next_start:
                    pass
                else:
                    ents.append(x)
                next_item_index = next_item_index + 1

            train_data = (
                plain_text,
                {
                    "entities": ents
                }
            )
            return train_data

    def create_tokenlist(self):

        """ returns a list of token-dicts extracted from tei:w, tei:pc and tei:seg """

        doc = self.tree
        expr = "//tei:*[local-name() = $name or local-name() = $pc]"
        words = doc.xpath(expr, name="w", pc="pc", namespaces=self.ns_tei)
        token_list = []
        for x in words:
            token = {}
            token['value'] = x.text
            token['tokenId'] = x.xpath('./@xml:id', namespaces=self.ns_tei)[0]
            try:
                if x.getnext().tag.endswith('seg'):
                    token['whitespace'] = True
                else:
                    token['whitespace'] = False
            except AttributeError:
                token['whitespace'] = False
            token_list.append(token)
        return token_list

    def process_tokenlist(self, tokenlist):

        """ takes a tokenlist and updated the tei:w tags. Returns the updated self.tree """

        expr = './/tei:w[@xml:id=$xmlid]'
        for x in tokenlist:
            try:
                node = self.tree.xpath(expr, xmlid=x['tokenId'], namespaces=self.nsmap)[0]
            except IndexError:
                node = None
            if node is not None:
                try:
                    node.attrib['lemma'] = x['lemma']
                except AttributeError:
                    pass
                try:
                    node.attrib['type'] = x['type']
                except AttributeError:
                    pass
                try:
                    node.attrib['ana'] = x['pos']
                except AttributeError:
                    pass

        return self.tree


def teis_to_traindata(
    files,
    start_node='.//tei:body',
    ne_xpath='.//tei:body//tei:rs',
    verbose=True
):

    """ extract NER-Train-Data from bunch of TEI files
        :param files: A list of file paths to TEI documents
        :param start_node: An XPath expressione pointing to\
        an element which text nodes should be extracted
        :param ne_xpath: An XPath expression pointing to elements used to tagged NEs.
        :return: A list of lists of spacy-like NER Tuple\
        [(('some text'), entities{[(15, 19, 'place')]}), (...)]
    """

    TRAIN_DATA = []
    for x in files:
        try:
            tei_doc = TeiReader(x)
            ners = tei_doc.extract_ne_offsets(start_node, ne_xpath)
            TRAIN_DATA.append(ners)
        except Exception as e:
            if verbose:
                print(e)
                print(x)

    return TRAIN_DATA
