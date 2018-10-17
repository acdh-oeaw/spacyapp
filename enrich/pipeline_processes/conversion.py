from enrich.tfc import Tcf
from enrich.tei import TeiReader
from enrich.custom_renderers import doc_to_tokenlist
from .base import check_validity_payload 


mapping_converters = {'from': {
    'application/xml+tei': (TeiReader, 'create_tokenlist'),
    'spacyDoc': (doc_to_tokenlist,),
    'application/xml+tcf': (Tcf, 'create_tokenlist')
},
    'to': {
        'application/xml+tei': (TeiReader, 'process_tokenlist')
    }
}


class Converter:

    def convert(self, to):
        if len(mapping_converters['to'][to]) == 2:
            self.data_converted = mapping_converters['to'][to][0](self.data_json)
            self.data_converted = getattr(self.data_converted, mapping_converters['to'][to][1])()
        else:
            self.data_converted = mapping_converters['to'][to][0](self.data_json)
        return self.data_converted

    def __init__(self, data_type=None, data=None):
        if data_type not in mapping_converters['from'].keys():
            raise ValueError('Data type specified is not supported by the converter.')
        if not check_validity_payload(data_type, data):
            raise ValueError('Payload has not the specified format.')
        if data_type == 'application/json+acdhlang':
            self.data_json = data
        elif len(mapping_converters['from'][data_type]) == 2:
            self.data_json = mapping_converters['from'][data_type][0](data)
            self.data_json = getattr(self.data, mapping_converters[data_type[1]])()
        else:
            self.data_json = mapping_converters['from'][data_type][0](data)
