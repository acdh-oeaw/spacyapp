from enrich.tfc import Tcf
from enrich.tei import TeiReader
from enrich.custom_renderers import doc_to_tokenlist
from enrich.custom_parsers import process_tokenlist
#from .base import check_validity_payload 


MAPPING_CONVERTERS_BAK = {'from': {
    'application/xml+tei': (TeiReader, 'create_tokenlist'),
    'spacyDoc': (doc_to_tokenlist,),
    'application/xml+tcf': (Tcf, 'create_tokenlist')
},
    'to': {
        'application/xml+tei': (TeiReader, 'process_tokenlist')
    }
}

MAPPING_CONVERTERS = {'from': {
    'application/xml+tei': (TeiReader, [('xml', 'original_xml')], 'create_tokenlist', [],),
    'spacyDoc': (doc_to_tokenlist, [('doc', 'payload')]),
    'application/xml+tcf': (Tcf, [('xml', 'original_xml')], 'create_tokenlist', [],)
},
    'to': {
        'application/xml+tei': (TeiReader, 'process_tokenlist'),
        'spacyDoc': (process_tokenlist, [('nlp', 'nlp'), ('tokenlist', '$data_json')])
    }
}


class Converter:

    def convert_bak(self, to):
        if len(MAPPING_CONVERTERS['to'][to]) == 2:
            self.data_converted = MAPPING_CONVERTERS['to'][to][0](self.data_json)
            self.data_converted = getattr(self.data_converted, MAPPING_CONVERTERS['to'][to][1])()
        else:
            self.data_converted = MAPPING_CONVERTERS['to'][to][0](self.data_json)
        return self.data_converted

    def _convert_internal(self, l, t):
        attr_dict = {}
        to = MAPPING_CONVERTERS[l][t]
        for d in to[1]:
            if d[1].startswith('$'):
                attr_dict[d[0]] = getattr(self, d[1][1:])
            else:
                attr_dict[d[0]] = getattr(self.original_process, d[1])
        print(attr_dict)
        data_converted = to[0](**attr_dict)
        if len(to) > 2:
            attr_dict = {}
            for d in to[3]:
                attr_dict[d[0]] = getattr(self.original_process, d[1])
            data_converted = getattr(data_converted, to[2])(**attr_dict)
        return data_converted

    def convert(self, to):
        self.data_converted = self._convert_internal('to', to)
        return self.data_converted
    
    def __init__(self, data_type=None, data=None, original_process=None):
        if data_type not in MAPPING_CONVERTERS['from'].keys() and data_type != 'application/json+acdhlang':
            raise ValueError('Data type specified is not supported by the converter.')
        if original_process is None:
            raise ValueError('Original process must be specified to get original files.')
        else:
            self.original_process = original_process
        if data_type == 'application/json+acdhlang':
            self.data_json = data
        else:
            self.data_json = self._convert_internal('from', data_type)
