import re


class Util(object):
    @classmethod
    def remove_label_and_callback(self, text):
        # 获取dwr回调函数的字符串
        dwr_callback = re.findall("dwr\.engine\._remoteHandleCallback\(.*\);\n", text)[0]
        # 去除dwr生成的js的回调函数
        text = text[:-len(dwr_callback)]

        # 去除Label
        text = re.sub("<\/{0,1}[a-z]+.*?>", '', text)

        return text
