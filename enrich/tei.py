import lxml.etree as ET

ns_tei = {'tei': "http://www.tei-c.org/ns/1.0"}
ns_xml = {'xml': "http://www.w3.org/XML/1998/namespace"}


class TeiReader():

    """ a class to read an process tei-documents"""

    def __init__(self, xml):
        self.ns_tei = {'tei': "http://www.tei-c.org/ns/1.0"}
        self.ns_xml = {'xml': "http://www.w3.org/XML/1998/namespace"}
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
