from functools import reduce
import operator


def get_from_path(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


def set_with_path(data_dict, map_list, value):
    get_from_path(data_dict, map_list[:-1])[map_list[-1]] = value
