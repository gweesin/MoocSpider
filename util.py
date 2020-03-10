import re


class Util(object):
    @classmethod
    def remove_label_and_callback(cls, text):
        # 获取dwr回调函数的字符串
        dwr_callback = re.findall("dwr\.engine\._remoteHandleCallback\(.*\);\n", text)[0]
        # 去除dwr生成的js的回调函数
        text = text[:-len(dwr_callback)]

        # 去除Label
        text = re.sub("<\/{0,1}[a-z]+.*?>", '', text)

        return text

    @classmethod
    def get_attr_value(cls, attr, text):
        """返回属性对应的精确值，例如找aid，找objectiveQList...

        :param attr: 要查找的属性
        :param text: 查找的范围
        :return: 返回对应的value
        """
        temp = re.findall(attr + ":*.[0-9]+,", text)[0]
        query_number = temp[len(attr) + 1: len(temp) - 1]

        return query_number
