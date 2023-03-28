import re
import json


def json_extraction(content):
    content = content.replace("\n", " ")
    # 定义正则表达式模式
    pattern = r"\[.*\]"
    # 匹配 JSON 数据
    match = re.search(pattern, content)
    if match:
        json_str = match.group()
        return json_str
    else:
        return None


def json2dicts(json_str):

    # 将单引号替换为双引号
    json_str = json_str.replace("'", "\"")

    print("======== "+json_str)

    # 解析 JSON 字符串为 Python 对象
    data = json.loads(json_str)

    # 将列表中的每个字典对象转换为 Python 字典
    result = []
    for item in data:
        result.append(dict(item))

    return result


def json2dict(json_str):
    # 解析 JSON 字符串为 Python 对象
    return json.loads(json_str)


def json_beautify(my_dicts):
    json_str = ""
    if type(my_dicts) == list:
        for my_dict in my_dicts:
            json_str += ("\n" + json.dumps(my_dict, ensure_ascii=False, indent=4))
    else:
        json_str += ("\n" + json.dumps(my_dicts, ensure_ascii=False, indent=4))
    return json_str



