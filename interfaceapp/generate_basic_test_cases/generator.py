#coding=utf-8


import time
import copy


def get_type_base_value(_type, _param):
    """根据类型获取基础测试的值"""
    if _type == 'string':
        return _param['string'].split(",")
    elif _type == 'date':
        return _param['date'].split(",")
    elif _type == 'int':
        return _param['int'].split(",")
    elif _type == 'decimal':
        return _param['decimal'].split(",")
    elif _type == 'bool':
        return _param['bool'].split(",")
    elif _type == 'number':
        return _param['number'].split(",")
    else:
        #  递归方法
        return recursive_case(_type, _param)


def create_base_case(_source, _param):
    all_data = {}
    for k, v in _source.items():
        for _value in get_type_base_value(v, _param):
            dic_cp2 = copy.deepcopy(_source)
            dic_cp2[k] = _value
            param_name = k + ":" + _value
            body = replace_default(dic_cp2)
            all_data[param_name] = body
    print("all_data:", all_data)
    return all_data


def recursive_case(_type, _param):
    """递归,返回特殊类型的取值范围"""
    if isinstance(_type, list):
        new_list = []
        if isinstance(_type[0], dict):
            t_value_list = create_base_case(_type[0], _param)  # 基础测试用例设计
            print("t_value_list:", t_value_list)
            for t_value in t_value_list:
                new_list.append([t_value])
        else:
            for _value in get_type_base_value(_type[0]):
                new_list.append([_value])
        print("new_list:", new_list)
        return new_list
    elif isinstance(_type, dict):
        return create_base_case(_type)
    else:
        return [None]


def replace_default(dic):
    """替换成默认值"""
    for k, v in dic.items():
        if isinstance(v, list):
            if isinstance(v[0], dict):
                dic[k] = [replace_default(v[0])]
            else:
                dic[k] = [default_value(v[0])]
        elif isinstance(v, dict):
            dic[k] = replace_default(v)
        else:
            dic[k] = default_value(v)
    return dic


def default_value(_type):
    if _type == 'string':
        return "default_string"
    elif _type == 'time':
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    elif _type == 'int':
        return 0
    elif _type == 'decimal':
        return 0.00
    elif _type == 'bool':
        return True
    elif _type == 'number':
        return 'default_number'
    else:
        return _type