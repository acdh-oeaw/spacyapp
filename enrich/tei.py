import lxml.etree as ET

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


class TeiReader(XMLReader):

    """ a class to read an process tei-documents"""

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
