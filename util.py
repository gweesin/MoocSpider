import re
from urllib.parse import quote


class Util(object):
    @classmethod
    def remove_label_and_callback(cls, text):
        # 获取dwr回调函数的字符串
        dwr_callback = re.findall("dwr\.engine\._remoteHandleCallback\(.*\);\n", text)
        # 去除dwr生成的js的回调函数
        if len(dwr_callback) is not 0:
            text = text[:-len(dwr_callback[0])]

        # 去除Label
        text = re.sub("<\/{0,1}[a-z]+.*?>", '', text)

        return text

    @classmethod
    def convert_html_blankspace(cls, text):
        text = re.sub('&nbsp;', ' ', text)
        return text

    @classmethod
    def convert_inner_label(cls, text):
        def convert2utf8(matched):
            tmp_str = matched.group('string')
            tmp_str = quote(tmp_str, encoding='utf-8')
            # print(tmp_str)
            return tmp_str

        text = re.sub("(?P<string><\/{0,1}[a-z]+.*>)", convert2utf8, text)

        def conver_plainTextTile2utf8(matched):
            tmp_str = matched.group('string')
            tmp_str = tmp_str[len("plainTextTitle="):len(tmp_str) - 1]
            tmp_str = quote(tmp_str, encoding='utf-8')
            print(tmp_str)
            return tmp_str

        # text = re.sub('(?P<string>plainTextTitle=".*?";)', conver_plainTextTile2utf8, text)
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

    @classmethod
    def convert2str(self, value):
        if value is None:
            return "null:null"
        if type(value) is int:
            return "number:%d" % value
        if type(value) is str:
            prefix_str = '<p><span style="font-family: 宋体; font-size: 16px;"  >'
            suffix_str = '</span></p>'
            # return "string:" + quote(prefix_str + value + suffix_str, encoding="utf-8")
            return quote(value, encoding="utf-8")
        return ''

    @classmethod
    def convert2req(cls, quiz_list, chapter_number):
        """
        option_obj: 对应需要转化的选项集
        """
        dict = {}
        result = []
        num = 5

        total_obj = "c0-e%d" % num
        num += 1
        dict[total_obj] = "Array:["
        # 把列表细化为每个quiz字典
        for quiz in quiz_list:
            quiz_list_obj = "c0-e%d" % num
            num += 1
            dict[quiz_list_obj] = "Object_Object:{"

            # 把每个quiz字典再细化
            for (quiz_key, quiz_value) in quiz.items():
                # 对于选项列表特殊处理
                if quiz_key == 'optionDtos':
                    # option是选项字典

                    quiz_obj = "c0-e%d" % num
                    num += 1
                    dict[quiz_obj] = "Array:["
                    for option in quiz_value:
                        option_obj = "c0-e%d" % num
                        num += 1
                        dict[option_obj] = "Object_Object:{"
                        # 分别处理option字典的每个字段
                        for (option_key, option_value) in option.items():
                            # print(option_key, option_value)
                            tmp = "c0-e%d=" % num + Util.convert2str(option_value)
                            dict[option_obj] += option_key + ":reference:c0-e%d," % num

                            num += 1
                            result.append(tmp)
                        dict[option_obj] = option_obj + "=" + dict[option_obj][:len(dict[option_obj]) - 1] + "}"
                        result.append(dict[option_obj])

                        dict[quiz_obj] += "reference:%s," % option_obj

                    if dict[quiz_obj] == "Array:[":
                        dict[quiz_obj] += ','
                    dict[quiz_obj] = quiz_obj + "=" + dict[quiz_obj][:len(dict[quiz_obj]) - 1] + "]"
                    result.append(dict[quiz_obj])

                    dict[quiz_list_obj] += quiz_key + ":reference:%s," % quiz_obj

                elif quiz_key == "optionsDetail":
                    continue
                elif quiz_key == "plainTextTitle":
                    # 对于普通的属性，正常处理
                    tmp = "c0-e%d=string:%s" % (num, quote(quiz_value, encoding='utf-8'))

                    dict[quiz_list_obj] += quiz_key + ":reference:c0-e%d," % num
                    result.append(tmp)
                    num += 1
                else:
                    # 对于普通的属性，正常处理
                    tmp = "c0-e%d=" % num + Util.convert2str(quiz_value)

                    dict[quiz_list_obj] += quiz_key + ":reference:c0-e%d," % num
                    result.append(tmp)
                    num += 1
            dict[quiz_list_obj] = quiz_list_obj + "=" + dict[quiz_list_obj][:len(dict[quiz_list_obj]) - 1] + "}"
            result.append(dict[quiz_list_obj])

            dict[total_obj] += "reference:%s," % quiz_list_obj

        if dict[total_obj] == 'Array:[':
            dict[total_obj] += ','
        dict[total_obj] = total_obj + "=" + dict[total_obj][:len(dict[total_obj]) - 1] + "]"
        result.append(dict[total_obj])

        num -= 1

        result.append("c0-e%d=boolean:true" % (num + 1))
        result.append("c0-e%d=Array:[]" % (num + 2))
        result.append("c0-e%d=number:1" % (num + 3))
        result.append("c0-e%d=number:%d" % (num + 4, int(chapter_number)))
        result.append("c0-e%d=string:" % (num + 5) + quote("绪论单元测试", encoding="utf-8"))
        result.append("c0-e%d=number:2" % (num + 6))
        result.append(
            "c0-param0=Object_Object:{" +
            "aid:reference:c0-e1,answers:reference:c0-e2,autoSubmit:reference:c0-e3,evaluateVo:reference:c0-e4," +
            "objectiveQList:reference:c0-e%d," % 5 +
            "showAnalysis:reference:c0-e%d," % (num + 1) +
            "subjectiveQList:reference:c0-e%d," % (num + 2) +
            "submitStatus:reference:c0-e%d," % (num + 3) +
            "tid:reference:c0-e%d," % (num + 4) +  # 这个地方我漏了一个e，气死了！！！！！！！！！！！！！！！！！！！！！！！！
            "tname:reference:c0-e%d," % (num + 5) +
            "type:reference:c0-e%d}" % (num + 6)
        )
        result.append("c0-param1=boolean:false")
        result.append("batchId=1583819197813")

        return '\n'.join(result)

    @classmethod
    def get_cookie_dict(cls):
        with open("cookie.txt", "r", encoding='utf-8') as f:
            cookies = f.read()
            dict = {}

            # 去空格和换行
            cookies = re.sub(' |\n', '', cookies)

            cookie_list = cookies.split(';')

            for cookie in cookie_list:
                tmp = cookie.split(sep='=', maxsplit=1)
                key, value = tmp[0], tmp[1]
                dict[key] = value
        return dict

if __name__ == '__main__':
    with open("test.txt", mode='r', encoding="utf-8") as f:
        string = f.read()
        string = Util.remove_label_and_callback(string)
        print(string)
