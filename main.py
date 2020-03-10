import requests
import re
import pprint
from exercise import Exercise, Option
import execjs
import pymongo
from util import Util


class MoocSpider(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Content-Type": "text/plain",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        self.cookies = {
            "EDUWEBDEVICE": "23398d07cfdc49f5899ea09bd954c4a5",
            "WM_TID": "XP1IV3hOpYlAAUVAAEZqQYiM6FnHbq2X",
            "__yadk_uid": "0afu1UBllLbDlkqVW1yclfu1NBqJHZld",
            "NTES_YD_PASSPORT": "Xll0WPvmB7y1H.zIr7oe.5skYDVUgrW0i2TDxLcAVLfVwsISwc4gjpUhAmaTEQkLeErFUQ7Qkta2oyWvWpnUERWUG2rVGtJ8evPAeglAwRPVozmTdFz0Ie5EgVjuxg0rBKfpT24LRktBrgcoyykMphgVhZ7YadJ6Q_9YM1i7s4R6EuvJtmg5L.Fbq9sz..dH9oSmLsESBxYQ97iOxgf0xwS_3",
            "P_INFO": "15959782573|1583414964|1|imooc|00&99|null&null&null#fuj&null#10#0|&0||15959782573",
            "hasVolume": "true",
            "videoResolutionType": "3",
            "videoRate": "1.75",
            "WM_NI": "stC3jhbpC2WMCltAY1bviCFpZiUjvtIk4NsbLbhaqUD7762FPk%2FUNqg%2FM1%2F7By5bXsVSYpNQtTmKUyWaRvdBHqN82aohwSDk7MYXpac7keX80qInZ49WZIeU6Y7uiQOIa0s%3D",
            "WM_NIKE": "9ca17ae2e6ffcda170e2e6eebbe85fa2eebeafd480afb48ea3d85e828a8eabf84b9be8a885e249938fa0d6d62af0fea7c3b92ab1ac8dd4e964a2b08dd3d64781b4bca2dc3ba2aaa7a4c57c9ab79b8bf5808bb5fcaff26a90bea882f45f88e9f9d7b14e94b5e1b6cd7ba5f183d2ae3d82a7fb83db79968d9791cd5bb88ca3acd87395bf9e97e74a8caf82d9b16badb8b9b4c761f59397b9f36ba1e9a586db34f4af878fd940fb8996aae85ff687f996ec5b8d97afd1f237e2a3",
            "videoVolume": "1",
            "NTESSTUDYSI": "40219d8c4ef84a0d9ba9e1c4ea95d0c5",
            "STUDY_INFO": "\"yd.981f1ed17b924e66a@163.com|8|1385959575|1583639750308\"",
            "STUDY_SESS": "\"2rYknfJqYdqYWXFIQIb3Cu4QcTZsfFYTKzEyH7Trrt7ybOgVMLblMZA56Vg55h0T2LvsqemS6Xmwq8f+sUJGLftxuo6MEHU9MDZ4Y5vTmY0NnGstLUlsck2odcumPeJDFnfS3C1xFmLMwuMm5p6RdvOQmngbCp8JtMfzQaE2/I0Lhur2Nm2wEb9HcEikV+3FTI8+lZKyHhiycNQo+g+/oA==\"",
            "STUDY_PERSIST": "\"Fclw9gZwcMNzEHNwOku/LzO4qf0vOBFVDiuIeL9UjPHRsUmIkCeL+eHTqyymsoS56SvXk+OASJ3PascNlawo+buFqWCG8+PBbtxfewuiwasa3jWCx4/rBohB5kKHNUMMyRX9xcrZ23i17fBj9H5GfdLr1/YxYKo1Nm06iM6uf5g9zkgB/nWz/K6q96X2gsM++7KesZvRP9O+NT2YNDZ2SfqMzIXzgy9p+Ou83dhh1PDZgpjCC7Iso4RP9U87vJE8LtaQzUT1ovP2MqtW5+L3Hw+PvH8+tZRDonbf7gEH7JU=\"",
            "NETEASE_WDA_UID": "1385959575#|#1551620478949"
        }
        self.base_url = "https://www.icourse163.org"

    def get_quiz_paper_dto(self, chapter_number='1224360494', quiz_number='1582379290', ):
        """获取测验页面上的题目、选项和答案

        Args:
            chapter_number: 章节号，quiz所属的章节
            quiz_number: 测验号，quiz的标识

        Returns:
            quiz_list: 测验的习题集（含答案）
        """

        request_data = "callCount=1\n" \
                       "scriptSessionId=${scriptSessionId}190\n" \
                       "httpSessionId=40219d8c4ef84a0d9ba9e1c4ea95d0c5\n" \
                       "c0-scriptName=MocQuizBean\n" \
                       "c0-methodName=getQuizPaperDto\n" \
                       "c0-id=0\n" \
                       "c0-param0=string:" + chapter_number + "\n" + \
                       "c0-param1=number:" + quiz_number + "\n" + \
                       "c0-param2=boolean:true\n" + \
                       "batchId=1"
        url = self.base_url + "/dwr/call/plaincall/MocQuizBean.getQuizPaperDto.dwr"
        requests.packages.urllib3.disable_warnings()
        res = requests.post(url=url, headers=self.headers, cookies=self.cookies, verify=False, data=request_data)
        res.encoding = 'unicode_escape'
        # print("测验页：\n" + res.text)

        # 去除html标签和dwr回调函数
        text = Util.remove_label_and_callback(res.text)
        js = execjs.compile(text)

        query_number = Util.get_attr_value("objectiveQList", res.text)

        quiz_list = js.eval(query_number)
        return quiz_list

        """2. 使用正则匹配
        # 匹配：s25.title="<p style="line-height: 150%;"  ><span style="font-size:16px;line-height:150%;font-family:宋体;"  >中国近代史和中国现代史的分界点是：</span></p>"
        complex_titles = re.findall('s[0-9]+.plainTextTitle=".*?";', res.text)

        for complex_title in complex_titles:
            # 练习题
            exercise = Exercise()
            # 匹配：>中国近代史和中国现代史的分界点是：
            # title = re.findall(">[0-9]*[^\x00-\xff]+", complex_title)[0][1:]
            temp = re.findall('".*"', complex_title)[0]
            title = temp[1:len(temp) - 1]
            # 匹配：s25.
            title_number = re.findall("s[0-9]+\.", complex_title)[0]
            title_number = title_number[:len(title_number) - 1]

            # 匹配：s25.optionDtos=s43
            temp = re.findall(title_number + "\.optionDtos=s[0-9]+", res.text)[0]
            # 匹配：s43
            temp_options_number = re.findall("=s[0-9]+", temp)[0][1:]
            # 先匹配：s43[0]=s44, s43[1]=s45... 再匹配：s44 s45...
            options_number_list = re.findall(temp_options_number + "\[[0-9]+\]=s[0-9]+", res.text)

            exercise.title = title
            for index in range(len(options_number_list)):
                # 获得每个选项对应的number
                options_number_list[index] = re.findall("s[0-9]+$", options_number_list[index])[0]

                option = Option()
                # 获取选项是否是答案
                temp = re.findall(options_number_list[index] + "\.answer=[a-z]", res.text)[0]
                if temp[len(temp) - 1] is 'f':
                    option.answer = False
                else:
                    option.answer = True

                # 获取选项内容
                temp = re.findall(options_number_list[index] + '\.content=".*"', res.text)[0]
                temp = re.findall(";\" {2}>.*<\/span>", temp)[0]
                option.content = temp[5:len(temp) - 7]
                exercise.options.append(option)

            exercise_list.append(exercise)
            print(exercise)
        """

    # 获取自己未做过的测验号quiz_number
    def get_new_quiz_number(self, chapter_number):
        request_data = "callCount=1\n" \
                       "scriptSessionId=${scriptSessionId}190\n" \
                       "httpSessionId=40219d8c4ef84a0d9ba9e1c4ea95d0c5\n" \
                       "c0-scriptName=MocQuizBean\n" \
                       "c0-methodName=getQuizPaperDto\n" \
                       "c0-id=0\n" \
                       "c0-param0=string:" + chapter_number + "\n" + \
                       "c0-param1=number:0\n" + \
                       "c0-param2=boolean:false\n" + \
                       "batchId=1"
        url = self.base_url + "/dwr/call/plaincall/MocQuizBean.getQuizPaperDto.dwr"
        requests.packages.urllib3.disable_warnings()
        res = requests.post(url=url, headers=self.headers, cookies=self.cookies, verify=False, data=request_data)
        res.encoding = 'unicode_escape'

        quiz_number = Util.get_attr_value("aid", res.text)
        return quiz_number

    # 获取具体chapter_number已做过的quiz_number列表
    def get_quiz_info(self, chapter_number):
        request_data = "callCount=1\n" \
                       "scriptSessionId=${scriptSessionId}190\n" \
                       "httpSessionId=40219d8c4ef84a0d9ba9e1c4ea95d0c5\n" \
                       "c0-scriptName=MocQuizBean\n" \
                       "c0-methodName=getQuizInfo\n" \
                       "c0-id=0\n" \
                       "c0-param0=string:" + chapter_number + "\n" + \
                       "c0-param1=null:null\n" + \
                       "c0-param2=boolean:false\n" + \
                       "batchId=1"
        requests.packages.urllib3.disable_warnings()
        url = self.base_url + "/dwr/call/plaincall/MocQuizBean.getQuizInfo.dwr"
        res = requests.post(url=url, headers=self.headers, cookies=self.cookies, verify=False, data=request_data)
        res.encoding = 'unicode_escape'

        # 得到['aid=1582379290', 'aid=1582494376', 'aid=1594652911', 'aid=1594652911']并去除"aid="
        temp_quiz_number = [x[4:] for x in re.findall('aid=[0-9]{2}[0-9]+', res.text)]
        # 去重
        quiz_number_list = []
        for x in temp_quiz_number:
            if x not in quiz_number_list:
                quiz_number_list.append(x)
        print("做过的测验题号：" + str(quiz_number_list))
        return quiz_number_list

    # 提交答案
    def submit_quiz_answer(self, quiz_number):
        """
        提交会返回错误的response，但是必须提交；
        后台有检测机制，如果没提交，下次申请的还是同一份测验题目，
        应该是为了让用户在断网重连之后，还能继续做同一份题
        """

        request_data = "callCount=1\n" + \
                       "scriptSessionId=${scriptSessionId}190\n" + \
                       "httpSessionId=40219d8c4ef84a0d9ba9e1c4ea95d0c5\n" + \
                       "c0-scriptName=MocQuizBean\n" + \
                       "c0-methodName=submitAnswers\n" + \
                       "c0-id=0\n" + \
                       "c0-e1=number:" + quiz_number + "\n" + \
                       "c0-e2=null:null\n" + \
                       "c0-e3=boolean:false\n" + \
                       "c0-e4=null:null\n" + \
                       "c0-e7=null:null\n" + \
                       "c0-e8=null:null\n" + \
                       "c0-e9=null:null\n" + \
                       "c0-e10=null:null\n" + \
                       "c0-e11=null:null\n" + \
                       "c0-e12=null:null\n" + \
                       "c0-e13=number:1235777986\n" + \
                       "c0-e14=null:null\n" + \
                       "c0-e15=null:null\n" + \
                       "c0-e16=null:null\n" + \
                       "c0-e17=null:null\n" + \
                       "c0-e18=null:null\n" + \
                       "c0-e19=null:null\n" + \
                       "c0-e20=null:null\n" + \
                       "c0-e21=null:null\n" + \
                       "c0-e22=null:null\n" + \
                       "c0-e25=null:null\n" + \
                       "c0-e26=null:null\n" + \
                       "c0-e27=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E9%9D%A9%E5%91%BD%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e28=number:68965768083785\n" + \
                       "c0-e24=Object_Object:{analyse:reference:c0-e25,answer:reference:c0-e26,content:reference:c0-e27,id:reference:c0-e28}\n" + \
                       "c0-e30=null:null\n" + \
                       "c0-e31=null:null\n" + \
                       "c0-e32=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E5%9B%BD%E5%AE%B6%E7%8B%AC%E7%AB%8B%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e33=number:368965768083785\n" + \
                       "c0-e29=Object_Object:{analyse:reference:c0-e30,answer:reference:c0-e31,content:reference:c0-e32,id:reference:c0-e33}\n" + \
                       "c0-e35=null:null\n" + \
                       "c0-e36=null:null\n" + \
                       "c0-e37=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E7%8E%B0%E4%BB%A3%E5%8C%96%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e38=number:168965768083785\n" + \
                       "c0-e34=Object_Object:{analyse:reference:c0-e35,answer:reference:c0-e36,content:reference:c0-e37,id:reference:c0-e38}\n" + \
                       "c0-e40=null:null\n" + \
                       "c0-e41=null:null\n" + \
                       "c0-e42=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E5%AE%9E%E7%8E%B0%E4%B8%AD%E5%8D%8E%E6%B0%91%E6%97%8F%E4%BC%9F%E5%A4%A7%E5%A4%8D%E5%85%B4%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e43=number:268965768083785\n" + \
                       "c0-e39=Object_Object:{analyse:reference:c0-e40,answer:reference:c0-e41,content:reference:c0-e42,id:reference:c0-e43}\n" + \
                       "c0-e23=Array:[reference:c0-e24,reference:c0-e29,reference:c0-e34,reference:c0-e39]\n" + \
                       "c0-e44=null:null\n" + \
                       "c0-e45=string:1840%E5%B9%B4%E4%BB%A5%E6%9D%A5%E8%87%B3%E4%BB%8A170%E5%A4%9A%E5%B9%B4%E4%B8%AD%E5%9B%BD%E8%BF%91%E7%8E%B0%E4%BB%A3%E5%8F%B2%E7%9A%84%E4%B8%BB%E9%A2%98%E6%98%AF%EF%BC%9A\n" + \
                       "c0-e46=number:2\n" + \
                       "c0-e47=null:null\n" + \
                       "c0-e48=null:null\n" + \
                       "c0-e49=number:2\n" + \
                       "c0-e50=null:null\n" + \
                       "c0-e51=null:null\n" + \
                       "c0-e52=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E1840%3C%2Fspan%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E5%B9%B4%E4%BB%A5%E6%9D%A5%E8%87%B3%E4%BB%8A170%E5%A4%9A%E5%B9%B4%E4%B8%AD%E5%9B%BD%E8%BF%91%E7%8E%B0%E4%BB%A3%E5%8F%B2%E7%9A%84%E4%B8%BB%E9%A2%98%E6%98%AF%EF%BC%9A%3C%2Fspan%3E%3C%2Fp%3E%3Cp%3E%3Cbr%20%3E%3C%2Fp%3E\n" + \
                       "c0-e53=null:null\n" + \
                       "c0-e54=null:null\n" + \
                       "c0-e55=number:1\n" + \
                       "c0-e6=Object_Object:{allowUpload:reference:c0-e7,analyse:reference:c0-e8,description:reference:c0-e9,fillblankType:reference:c0-e10,gmtCreate:reference:c0-e11,gmtModified:reference:c0-e12,id:reference:c0-e13,judgeDtos:reference:c0-e14,judgerules:reference:c0-e15,ojCases:reference:c0-e16,ojMemLimit:reference:c0-e17,ojNeedInput:reference:c0-e18,ojSupportedLanguage:reference:c0-e19,ojSupportedLanguageList:reference:c0-e20,ojTimeLimit:reference:c0-e21,ojTryTime:reference:c0-e22,optionDtos:reference:c0-e23,options:reference:c0-e44,plainTextTitle:reference:c0-e45,position:reference:c0-e46,sampleAnswerJson:reference:c0-e47,sampleAnswers:reference:c0-e48,score:reference:c0-e49,stdAnswer:reference:c0-e50,testId:reference:c0-e51,title:reference:c0-e52,titleAttachment:reference:c0-e53,titleAttachmentDtos:reference:c0-e54,type:reference:c0-e55}\n" + \
                       "c0-e57=null:null\n" + \
                       "c0-e58=null:null\n" + \
                       "c0-e59=null:null\n" + \
                       "c0-e60=null:null\n" + \
                       "c0-e61=null:null\n" + \
                       "c0-e62=null:null\n" + \
                       "c0-e63=number:1235777988\n" + \
                       "c0-e64=null:null\n" + \
                       "c0-e65=null:null\n" + \
                       "c0-e66=null:null\n" + \
                       "c0-e67=null:null\n" + \
                       "c0-e68=null:null\n" + \
                       "c0-e69=null:null\n" + \
                       "c0-e70=null:null\n" + \
                       "c0-e71=null:null\n" + \
                       "c0-e72=null:null\n" + \
                       "c0-e75=null:null\n" + \
                       "c0-e76=null:null\n" + \
                       "c0-e77=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E6%96%AF%E5%A4%A7%E6%9E%97%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e78=number:265063522075596\n" + \
                       "c0-e74=Object_Object:{analyse:reference:c0-e75,answer:reference:c0-e76,content:reference:c0-e77,id:reference:c0-e78}\n" + \
                       "c0-e80=null:null\n" + \
                       "c0-e81=null:null\n" + \
                       "c0-e82=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E6%81%A9%E6%A0%BC%E6%96%AF%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e83=number:65063522075596\n" + \
                       "c0-e79=Object_Object:{analyse:reference:c0-e80,answer:reference:c0-e81,content:reference:c0-e82,id:reference:c0-e83}\n" + \
                       "c0-e85=null:null\n" + \
                       "c0-e86=null:null\n" + \
                       "c0-e87=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E5%88%97%E5%AE%81%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e88=number:165063522075596\n" + \
                       "c0-e84=Object_Object:{analyse:reference:c0-e85,answer:reference:c0-e86,content:reference:c0-e87,id:reference:c0-e88}\n" + \
                       "c0-e90=null:null\n" + \
                       "c0-e91=null:null\n" + \
                       "c0-e92=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E4%BC%AF%E6%81%A9%E6%96%AF%E5%9D%A6%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e93=number:365063522075596\n" + \
                       "c0-e89=Object_Object:{analyse:reference:c0-e90,answer:reference:c0-e91,content:reference:c0-e92,id:reference:c0-e93}\n" + \
                       "c0-e73=Array:[reference:c0-e74,reference:c0-e79,reference:c0-e84,reference:c0-e89]\n" + \
                       "c0-e94=null:null\n" + \
                       "c0-e95=string:%E6%8F%90%E5%87%BA%E9%A9%AC%E5%85%8B%E6%80%9D%E4%B8%BB%E4%B9%89%E7%9A%84%E5%94%AF%E7%89%A9%E5%8F%B2%E8%A7%82%E6%98%AF%E2%80%9C%E5%94%AF%E4%B8%80%E7%9A%84%E7%A7%91%E5%AD%A6%E7%9A%84%E5%8E%86%E5%8F%B2%E8%A7%82%E2%80%9D%E7%9A%84%E6%98%AF%EF%BC%9A\n" + \
                       "c0-e96=number:4\n" + \
                       "c0-e97=null:null\n" + \
                       "c0-e98=null:null\n" + \
                       "c0-e99=number:2\n" + \
                       "c0-e100=null:null\n" + \
                       "c0-e101=null:null\n" + \
                       "c0-e102=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E6%8F%90%E5%87%BA%E9%A9%AC%E5%85%8B%E6%80%9D%E4%B8%BB%E4%B9%89%E7%9A%84%E5%94%AF%E7%89%A9%E5%8F%B2%E8%A7%82%E6%98%AF%E2%80%9C%E5%94%AF%E4%B8%80%E7%9A%84%E7%A7%91%E5%AD%A6%E7%9A%84%E5%8E%86%E5%8F%B2%E8%A7%82%E2%80%9D%E7%9A%84%E6%98%AF%EF%BC%9A%3C%2Fspan%3E%3C%2Fp%3E%3Cp%3E%3Cbr%20%3E%3C%2Fp%3E\n" + \
                       "c0-e103=null:null\n" + \
                       "c0-e104=null:null\n" + \
                       "c0-e105=number:1\n" + \
                       "c0-e56=Object_Object:{allowUpload:reference:c0-e57,analyse:reference:c0-e58,description:reference:c0-e59,fillblankType:reference:c0-e60,gmtCreate:reference:c0-e61,gmtModified:reference:c0-e62,id:reference:c0-e63,judgeDtos:reference:c0-e64,judgerules:reference:c0-e65,ojCases:reference:c0-e66,ojMemLimit:reference:c0-e67,ojNeedInput:reference:c0-e68,ojSupportedLanguage:reference:c0-e69,ojSupportedLanguageList:reference:c0-e70,ojTimeLimit:reference:c0-e71,ojTryTime:reference:c0-e72,optionDtos:reference:c0-e73,options:reference:c0-e94,plainTextTitle:reference:c0-e95,position:reference:c0-e96,sampleAnswerJson:reference:c0-e97,sampleAnswers:reference:c0-e98,score:reference:c0-e99,stdAnswer:reference:c0-e100,testId:reference:c0-e101,title:reference:c0-e102,titleAttachment:reference:c0-e103,titleAttachmentDtos:reference:c0-e104,type:reference:c0-e105}\n" + \
                       "c0-e107=null:null\n" + \
                       "c0-e108=null:null\n" + \
                       "c0-e109=null:null\n" + \
                       "c0-e110=null:null\n" + \
                       "c0-e111=null:null\n" + \
                       "c0-e112=null:null\n" + \
                       "c0-e113=number:1235777989\n" + \
                       "c0-e114=null:null\n" + \
                       "c0-e115=null:null\n" + \
                       "c0-e116=null:null\n" + \
                       "c0-e117=null:null\n" + \
                       "c0-e118=null:null\n" + \
                       "c0-e119=null:null\n" + \
                       "c0-e120=null:null\n" + \
                       "c0-e121=null:null\n" + \
                       "c0-e122=null:null\n" + \
                       "c0-e125=null:null\n" + \
                       "c0-e126=null:null\n" + \
                       "c0-e127=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E7%8E%8B%E5%85%85%26nbsp%3B%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e128=number:265063571095753\n" + \
                       "c0-e124=Object_Object:{analyse:reference:c0-e125,answer:reference:c0-e126,content:reference:c0-e127,id:reference:c0-e128}\n" + \
                       "c0-e130=null:null\n" + \
                       "c0-e131=null:null\n" + \
                       "c0-e132=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E9%AD%8F%E5%BE%81%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e133=number:365063571095753\n" + \
                       "c0-e129=Object_Object:{analyse:reference:c0-e130,answer:reference:c0-e131,content:reference:c0-e132,id:reference:c0-e133}\n" + \
                       "c0-e135=null:null\n" + \
                       "c0-e136=null:null\n" + \
                       "c0-e137=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E5%AD%94%E5%AD%90%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e138=number:65063571095753\n" + \
                       "c0-e134=Object_Object:{analyse:reference:c0-e135,answer:reference:c0-e136,content:reference:c0-e137,id:reference:c0-e138}\n" + \
                       "c0-e140=null:null\n" + \
                       "c0-e141=null:null\n" + \
                       "c0-e142=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E5%AD%9F%E5%AD%90%26nbsp%3B%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e143=number:165063571095753\n" + \
                       "c0-e139=Object_Object:{analyse:reference:c0-e140,answer:reference:c0-e141,content:reference:c0-e142,id:reference:c0-e143}\n" + \
                       "c0-e123=Array:[reference:c0-e124,reference:c0-e129,reference:c0-e134,reference:c0-e139]\n" + \
                       "c0-e144=null:null\n" + \
                       "c0-e145=string:%E6%8F%90%E5%87%BA%E2%80%9C%E6%98%8E%E9%95%9C%E6%89%80%E4%BB%A5%E5%AF%9F%E5%BD%A2%EF%BC%8C%E5%BE%80%E5%8F%A4%E8%80%85%E6%89%80%E4%BB%A5%E7%9F%A5%E4%BB%8A%E2%80%9D%E7%9A%84%E6%80%9D%E6%83%B3%E5%AE%B6%E6%98%AF%3A\n" + \
                       "c0-e146=number:5\n" + \
                       "c0-e147=null:null\n" + \
                       "c0-e148=null:null\n" + \
                       "c0-e149=number:2\n" + \
                       "c0-e150=null:null\n" + \
                       "c0-e151=null:null\n" + \
                       "c0-e152=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E6%8F%90%E5%87%BA%E2%80%9C%E6%98%8E%E9%95%9C%E6%89%80%E4%BB%A5%E5%AF%9F%E5%BD%A2%EF%BC%8C%E5%BE%80%E5%8F%A4%E8%80%85%E6%89%80%E4%BB%A5%E7%9F%A5%E4%BB%8A%E2%80%9D%E7%9A%84%E6%80%9D%E6%83%B3%E5%AE%B6%E6%98%AF%3A%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e153=null:null\n" + \
                       "c0-e154=null:null\n" + \
                       "c0-e155=number:1\n" + \
                       "c0-e106=Object_Object:{allowUpload:reference:c0-e107,analyse:reference:c0-e108,description:reference:c0-e109,fillblankType:reference:c0-e110,gmtCreate:reference:c0-e111,gmtModified:reference:c0-e112,id:reference:c0-e113,judgeDtos:reference:c0-e114,judgerules:reference:c0-e115,ojCases:reference:c0-e116,ojMemLimit:reference:c0-e117,ojNeedInput:reference:c0-e118,ojSupportedLanguage:reference:c0-e119,ojSupportedLanguageList:reference:c0-e120,ojTimeLimit:reference:c0-e121,ojTryTime:reference:c0-e122,optionDtos:reference:c0-e123,options:reference:c0-e144,plainTextTitle:reference:c0-e145,position:reference:c0-e146,sampleAnswerJson:reference:c0-e147,sampleAnswers:reference:c0-e148,score:reference:c0-e149,stdAnswer:reference:c0-e150,testId:reference:c0-e151,title:reference:c0-e152,titleAttachment:reference:c0-e153,titleAttachmentDtos:reference:c0-e154,type:reference:c0-e155}\n" + \
                       "c0-e157=null:null\n" + \
                       "c0-e158=null:null\n" + \
                       "c0-e159=null:null\n" + \
                       "c0-e160=null:null\n" + \
                       "c0-e161=null:null\n" + \
                       "c0-e162=null:null\n" + \
                       "c0-e163=number:1235777990\n" + \
                       "c0-e164=null:null\n" + \
                       "c0-e165=null:null\n" + \
                       "c0-e166=null:null\n" + \
                       "c0-e167=null:null\n" + \
                       "c0-e168=null:null\n" + \
                       "c0-e169=null:null\n" + \
                       "c0-e170=null:null\n" + \
                       "c0-e171=null:null\n" + \
                       "c0-e172=null:null\n" + \
                       "c0-e175=null:null\n" + \
                       "c0-e176=null:null\n" + \
                       "c0-e177=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E4%B8%8D%E8%83%BD%E4%BB%A5%E7%A2%8E%E7%89%87%E5%8C%96%E7%9A%84%E5%8E%86%E5%8F%B2%E7%BB%86%E8%8A%82%E5%BE%97%E5%87%BA%E6%95%B4%E4%BD%93%E5%8E%86%E5%8F%B2%E7%9A%84%E7%BB%93%E8%AE%BA%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e178=number:368965989316913\n" + \
                       "c0-e174=Object_Object:{analyse:reference:c0-e175,answer:reference:c0-e176,content:reference:c0-e177,id:reference:c0-e178}\n" + \
                       "c0-e180=null:null\n" + \
                       "c0-e181=null:null\n" + \
                       "c0-e182=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E5%BF%85%E9%A1%BB%E6%8A%8A%E5%85%B7%E4%BD%93%E7%9A%84%E5%8E%86%E5%8F%B2%E4%BA%8B%E4%BB%B6%E6%94%BE%E5%9C%A8%E5%8E%86%E5%8F%B2%E5%8F%91%E5%B1%95%E7%9A%84%E5%85%A8%E8%BF%87%E7%A8%8B%E4%B8%AD%E8%BF%9B%E8%A1%8C%E8%80%83%E5%AF%9F%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e183=number:268965989316913\n" + \
                       "c0-e179=Object_Object:{analyse:reference:c0-e180,answer:reference:c0-e181,content:reference:c0-e182,id:reference:c0-e183}\n" + \
                       "c0-e185=null:null\n" + \
                       "c0-e186=null:null\n" + \
                       "c0-e187=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E5%8F%AA%E6%9C%89%E4%BA%86%E8%A7%A3%E5%8E%86%E5%8F%B2%E7%9A%84%E7%9C%9F%E7%9B%B8%E6%89%8D%E8%83%BD%E5%BE%97%E5%87%BA%E6%AD%A3%E7%A1%AE%E7%9A%84%E7%BB%93%E8%AE%BA%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e188=number:168965989316913\n" + \
                       "c0-e184=Object_Object:{analyse:reference:c0-e185,answer:reference:c0-e186,content:reference:c0-e187,id:reference:c0-e188}\n" + \
                       "c0-e190=null:null\n" + \
                       "c0-e191=null:null\n" + \
                       "c0-e192=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E5%BF%85%E9%A1%BB%E5%85%85%E5%88%86%E7%9A%84%E6%8E%8C%E6%8F%A1%E5%8E%86%E5%8F%B2%E6%9D%90%E6%96%99%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e193=number:68965989316913\n" + \
                       "c0-e189=Object_Object:{analyse:reference:c0-e190,answer:reference:c0-e191,content:reference:c0-e192,id:reference:c0-e193}\n" + \
                       "c0-e173=Array:[reference:c0-e174,reference:c0-e179,reference:c0-e184,reference:c0-e189]\n" + \
                       "c0-e194=null:null\n" + \
                       "c0-e195=string:%E7%94%B1%E2%80%9C%E7%9B%B2%E4%BA%BA%E6%91%B8%E8%B1%A1%E2%80%9D%E7%9A%84%E6%95%85%E4%BA%8B%E5%AF%B9%E4%BA%8E%E6%88%91%E4%BB%AC%E5%AD%A6%E4%B9%A0%E5%8E%86%E5%8F%B2%E6%9C%80%E9%87%8D%E8%A6%81%E7%9A%84%E5%90%AF%E7%A4%BA%E6%98%AF%EF%BC%9A\n" + \
                       "c0-e196=number:6\n" + \
                       "c0-e197=null:null\n" + \
                       "c0-e198=null:null\n" + \
                       "c0-e199=number:2\n" + \
                       "c0-e200=null:null\n" + \
                       "c0-e201=null:null\n" + \
                       "c0-e202=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E7%94%B1%E2%80%9C%E7%9B%B2%E4%BA%BA%E6%91%B8%E8%B1%A1%E2%80%9D%E7%9A%84%E6%95%85%E4%BA%8B%E5%AF%B9%E4%BA%8E%E6%88%91%E4%BB%AC%E5%AD%A6%E4%B9%A0%E5%8E%86%E5%8F%B2%E6%9C%80%E9%87%8D%E8%A6%81%E7%9A%84%E5%90%AF%E7%A4%BA%E6%98%AF%EF%BC%9A%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e203=null:null\n" + \
                       "c0-e204=null:null\n" + \
                       "c0-e205=number:1\n" + \
                       "c0-e156=Object_Object:{allowUpload:reference:c0-e157,analyse:reference:c0-e158,description:reference:c0-e159,fillblankType:reference:c0-e160,gmtCreate:reference:c0-e161,gmtModified:reference:c0-e162,id:reference:c0-e163,judgeDtos:reference:c0-e164,judgerules:reference:c0-e165,ojCases:reference:c0-e166,ojMemLimit:reference:c0-e167,ojNeedInput:reference:c0-e168,ojSupportedLanguage:reference:c0-e169,ojSupportedLanguageList:reference:c0-e170,ojTimeLimit:reference:c0-e171,ojTryTime:reference:c0-e172,optionDtos:reference:c0-e173,options:reference:c0-e194,plainTextTitle:reference:c0-e195,position:reference:c0-e196,sampleAnswerJson:reference:c0-e197,sampleAnswers:reference:c0-e198,score:reference:c0-e199,stdAnswer:reference:c0-e200,testId:reference:c0-e201,title:reference:c0-e202,titleAttachment:reference:c0-e203,titleAttachmentDtos:reference:c0-e204,type:reference:c0-e205}\n" + \
                       "c0-e207=null:null\n" + \
                       "c0-e208=null:null\n" + \
                       "c0-e209=null:null\n" + \
                       "c0-e210=null:null\n" + \
                       "c0-e211=null:null\n" + \
                       "c0-e212=null:null\n" + \
                       "c0-e213=number:1235777991\n" + \
                       "c0-e214=null:null\n" + \
                       "c0-e215=null:null\n" + \
                       "c0-e216=null:null\n" + \
                       "c0-e217=null:null\n" + \
                       "c0-e218=null:null\n" + \
                       "c0-e219=null:null\n" + \
                       "c0-e220=null:null\n" + \
                       "c0-e221=null:null\n" + \
                       "c0-e222=null:null\n" + \
                       "c0-e225=null:null\n" + \
                       "c0-e226=null:null\n" + \
                       "c0-e227=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E7%A4%BE%E4%BC%9A%E4%B8%BB%E4%B9%89%E6%94%B9%E9%80%A0%E7%9A%84%E5%AE%8C%E6%88%90%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e228=number:268971243486713\n" + \
                       "c0-e224=Object_Object:{analyse:reference:c0-e225,answer:reference:c0-e226,content:reference:c0-e227,id:reference:c0-e228}\n" + \
                       "c0-e230=null:null\n" + \
                       "c0-e231=null:null\n" + \
                       "c0-e232=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E4%B8%AD%E5%9B%BD%E5%85%B1%E4%BA%A7%E5%85%9A%E7%9A%84%E6%88%90%E7%AB%8B%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e233=number:168971243486713\n" + \
                       "c0-e229=Object_Object:{analyse:reference:c0-e230,answer:reference:c0-e231,content:reference:c0-e232,id:reference:c0-e233}\n" + \
                       "c0-e235=null:null\n" + \
                       "c0-e236=null:null\n" + \
                       "c0-e237=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E8%BE%9B%E4%BA%A5%E9%9D%A9%E5%91%BD%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e238=number:68971243486713\n" + \
                       "c0-e234=Object_Object:{analyse:reference:c0-e235,answer:reference:c0-e236,content:reference:c0-e237,id:reference:c0-e238}\n" + \
                       "c0-e240=null:null\n" + \
                       "c0-e241=null:null\n" + \
                       "c0-e242=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E6%94%B9%E9%9D%A9%E5%BC%80%E6%94%BE%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e243=number:368971243486713\n" + \
                       "c0-e239=Object_Object:{analyse:reference:c0-e240,answer:reference:c0-e241,content:reference:c0-e242,id:reference:c0-e243}\n" + \
                       "c0-e223=Array:[reference:c0-e224,reference:c0-e229,reference:c0-e234,reference:c0-e239]\n" + \
                       "c0-e244=null:null\n" + \
                       "c0-e245=string:%E4%B9%A0%E5%B9%B3%E6%80%BB%E4%B9%A6%E8%AE%B0%E6%89%80%E8%AF%B4%E7%9A%84%E2%80%9C%E6%B7%B1%E5%88%BB%E6%94%B9%E5%8F%98%E8%BF%91%E4%BB%A3%E4%BB%A5%E5%90%8E%E4%B8%AD%E5%8D%8E%E6%B0%91%E6%97%8F%E5%8F%91%E5%B1%95%E7%9A%84%E6%96%B9%E5%90%91%E5%92%8C%E8%BF%9B%E7%A8%8B%EF%BC%8C%E6%B7%B1%E5%88%BB%E6%94%B9%E5%8F%98%E4%BA%86%E4%B8%AD%E5%9B%BD%E4%BA%BA%E6%B0%91%E5%92%8C%E4%B8%AD%E5%8D%8E%E6%B0%91%E6%97%8F%E7%9A%84%E5%89%8D%E9%80%94%E5%92%8C%E5%91%BD%E8%BF%90%E2%80%9D%E7%9A%84%E9%87%8D%E5%A4%A7%E5%8E%86%E5%8F%B2%E4%BA%8B%E4%BB%B6%E6%98%AF%E6%8C%87%EF%BC%9A\n" + \
                       "c0-e246=number:7\n" + \
                       "c0-e247=null:null\n" + \
                       "c0-e248=null:null\n" + \
                       "c0-e249=number:2\n" + \
                       "c0-e250=null:null\n" + \
                       "c0-e251=null:null\n" + \
                       "c0-e252=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E4%B9%A0%E5%B9%B3%E6%80%BB%E4%B9%A6%E8%AE%B0%E6%89%80%E8%AF%B4%E7%9A%84%E2%80%9C%E6%B7%B1%E5%88%BB%E6%94%B9%E5%8F%98%E8%BF%91%E4%BB%A3%E4%BB%A5%E5%90%8E%E4%B8%AD%E5%8D%8E%E6%B0%91%E6%97%8F%E5%8F%91%E5%B1%95%E7%9A%84%E6%96%B9%E5%90%91%E5%92%8C%E8%BF%9B%E7%A8%8B%EF%BC%8C%E6%B7%B1%E5%88%BB%E6%94%B9%E5%8F%98%E4%BA%86%E4%B8%AD%E5%9B%BD%E4%BA%BA%E6%B0%91%E5%92%8C%E4%B8%AD%E5%8D%8E%E6%B0%91%E6%97%8F%E7%9A%84%E5%89%8D%E9%80%94%E5%92%8C%E5%91%BD%E8%BF%90%E2%80%9D%E7%9A%84%E9%87%8D%E5%A4%A7%E5%8E%86%E5%8F%B2%E4%BA%8B%E4%BB%B6%E6%98%AF%E6%8C%87%EF%BC%9A%3C%2Fspan%3E%3C%2Fp%3E%3Cp%3E%3Cbr%20%3E%3C%2Fp%3E\n" + \
                       "c0-e253=null:null\n" + \
                       "c0-e254=null:null\n" + \
                       "c0-e255=number:1\n" + \
                       "c0-e206=Object_Object:{allowUpload:reference:c0-e207,analyse:reference:c0-e208,description:reference:c0-e209,fillblankType:reference:c0-e210,gmtCreate:reference:c0-e211,gmtModified:reference:c0-e212,id:reference:c0-e213,judgeDtos:reference:c0-e214,judgerules:reference:c0-e215,ojCases:reference:c0-e216,ojMemLimit:reference:c0-e217,ojNeedInput:reference:c0-e218,ojSupportedLanguage:reference:c0-e219,ojSupportedLanguageList:reference:c0-e220,ojTimeLimit:reference:c0-e221,ojTryTime:reference:c0-e222,optionDtos:reference:c0-e223,options:reference:c0-e244,plainTextTitle:reference:c0-e245,position:reference:c0-e246,sampleAnswerJson:reference:c0-e247,sampleAnswers:reference:c0-e248,score:reference:c0-e249,stdAnswer:reference:c0-e250,testId:reference:c0-e251,title:reference:c0-e252,titleAttachment:reference:c0-e253,titleAttachmentDtos:reference:c0-e254,type:reference:c0-e255}\n" + \
                       "c0-e257=null:null\n" + \
                       "c0-e258=null:null\n" + \
                       "c0-e259=null:null\n" + \
                       "c0-e260=null:null\n" + \
                       "c0-e261=null:null\n" + \
                       "c0-e262=null:null\n" + \
                       "c0-e263=number:1235777992\n" + \
                       "c0-e264=null:null\n" + \
                       "c0-e265=null:null\n" + \
                       "c0-e266=null:null\n" + \
                       "c0-e267=null:null\n" + \
                       "c0-e268=null:null\n" + \
                       "c0-e269=null:null\n" + \
                       "c0-e270=null:null\n" + \
                       "c0-e271=null:null\n" + \
                       "c0-e272=null:null\n" + \
                       "c0-e275=null:null\n" + \
                       "c0-e276=null:null\n" + \
                       "c0-e277=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E1840%E5%B9%B4%E8%87%B31919%E5%B9%B4%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e278=number:165063743653428\n" + \
                       "c0-e274=Object_Object:{analyse:reference:c0-e275,answer:reference:c0-e276,content:reference:c0-e277,id:reference:c0-e278}\n" + \
                       "c0-e280=null:null\n" + \
                       "c0-e281=null:null\n" + \
                       "c0-e282=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E1840%E5%B9%B4%E8%87%B31949%E5%B9%B4%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e283=number:365063743653428\n" + \
                       "c0-e279=Object_Object:{analyse:reference:c0-e280,answer:reference:c0-e281,content:reference:c0-e282,id:reference:c0-e283}\n" + \
                       "c0-e285=null:null\n" + \
                       "c0-e286=null:null\n" + \
                       "c0-e287=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E1840%E5%B9%B4%E8%87%B31945%E5%B9%B4%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e288=number:265063743653428\n" + \
                       "c0-e284=Object_Object:{analyse:reference:c0-e285,answer:reference:c0-e286,content:reference:c0-e287,id:reference:c0-e288}\n" + \
                       "c0-e290=null:null\n" + \
                       "c0-e291=null:null\n" + \
                       "c0-e292=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E1840%E5%B9%B4%E8%87%B31911%E5%B9%B4%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e293=number:65063743653428\n" + \
                       "c0-e289=Object_Object:{analyse:reference:c0-e290,answer:reference:c0-e291,content:reference:c0-e292,id:reference:c0-e293}\n" + \
                       "c0-e273=Array:[reference:c0-e274,reference:c0-e279,reference:c0-e284,reference:c0-e289]\n" + \
                       "c0-e294=null:null\n" + \
                       "c0-e295=string:%E4%B8%AD%E5%9B%BD%E8%BF%91%E4%BB%A3%E5%8F%B2%E6%97%B6%E6%9C%9F%E6%98%AF%E6%8C%87%EF%BC%9A\n" + \
                       "c0-e296=number:8\n" + \
                       "c0-e297=null:null\n" + \
                       "c0-e298=null:null\n" + \
                       "c0-e299=number:2\n" + \
                       "c0-e300=null:null\n" + \
                       "c0-e301=null:null\n" + \
                       "c0-e302=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E4%B8%AD%E5%9B%BD%E8%BF%91%E4%BB%A3%E5%8F%B2%E6%97%B6%E6%9C%9F%E6%98%AF%E6%8C%87%EF%BC%9A%3C%2Fspan%3E%3C%2Fp%3E%3Cp%3E%3Cbr%20%3E%3C%2Fp%3E\n" + \
                       "c0-e303=null:null\n" + \
                       "c0-e304=null:null\n" + \
                       "c0-e305=number:1\n" + \
                       "c0-e256=Object_Object:{allowUpload:reference:c0-e257,analyse:reference:c0-e258,description:reference:c0-e259,fillblankType:reference:c0-e260,gmtCreate:reference:c0-e261,gmtModified:reference:c0-e262,id:reference:c0-e263,judgeDtos:reference:c0-e264,judgerules:reference:c0-e265,ojCases:reference:c0-e266,ojMemLimit:reference:c0-e267,ojNeedInput:reference:c0-e268,ojSupportedLanguage:reference:c0-e269,ojSupportedLanguageList:reference:c0-e270,ojTimeLimit:reference:c0-e271,ojTryTime:reference:c0-e272,optionDtos:reference:c0-e273,options:reference:c0-e294,plainTextTitle:reference:c0-e295,position:reference:c0-e296,sampleAnswerJson:reference:c0-e297,sampleAnswers:reference:c0-e298,score:reference:c0-e299,stdAnswer:reference:c0-e300,testId:reference:c0-e301,title:reference:c0-e302,titleAttachment:reference:c0-e303,titleAttachmentDtos:reference:c0-e304,type:reference:c0-e305}\n" + \
                       "c0-e307=null:null\n" + \
                       "c0-e308=null:null\n" + \
                       "c0-e309=null:null\n" + \
                       "c0-e310=null:null\n" + \
                       "c0-e311=null:null\n" + \
                       "c0-e312=null:null\n" + \
                       "c0-e313=number:1235777993\n" + \
                       "c0-e314=null:null\n" + \
                       "c0-e315=null:null\n" + \
                       "c0-e316=null:null\n" + \
                       "c0-e317=null:null\n" + \
                       "c0-e318=null:null\n" + \
                       "c0-e319=null:null\n" + \
                       "c0-e320=null:null\n" + \
                       "c0-e321=null:null\n" + \
                       "c0-e322=null:null\n" + \
                       "c0-e325=null:null\n" + \
                       "c0-e326=null:null\n" + \
                       "c0-e327=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E6%9D%A8%E5%BA%A6%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e328=number:365063787569014\n" + \
                       "c0-e324=Object_Object:{analyse:reference:c0-e325,answer:reference:c0-e326,content:reference:c0-e327,id:reference:c0-e328}\n" + \
                       "c0-e330=null:null\n" + \
                       "c0-e331=null:null\n" + \
                       "c0-e332=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E6%A2%81%E5%90%AF%E8%B6%85%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e333=number:165063787569014\n" + \
                       "c0-e329=Object_Object:{analyse:reference:c0-e330,answer:reference:c0-e331,content:reference:c0-e332,id:reference:c0-e333}\n" + \
                       "c0-e335=null:null\n" + \
                       "c0-e336=null:null\n" + \
                       "c0-e337=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E5%BA%B7%E6%9C%89%E4%B8%BA%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e338=number:65063787569014\n" + \
                       "c0-e334=Object_Object:{analyse:reference:c0-e335,answer:reference:c0-e336,content:reference:c0-e337,id:reference:c0-e338}\n" + \
                       "c0-e340=null:null\n" + \
                       "c0-e341=null:null\n" + \
                       "c0-e342=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2032px%3B%22%20%20%3E%E5%AD%99%E4%B8%AD%E5%B1%B1%26nbsp%3B%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e343=number:265063787569014\n" + \
                       "c0-e339=Object_Object:{analyse:reference:c0-e340,answer:reference:c0-e341,content:reference:c0-e342,id:reference:c0-e343}\n" + \
                       "c0-e323=Array:[reference:c0-e324,reference:c0-e329,reference:c0-e334,reference:c0-e339]\n" + \
                       "c0-e344=null:null\n" + \
                       "c0-e345=string:%E4%B8%AD%E5%9B%BD%E8%BF%91%E4%BB%A3%E6%9C%80%E6%97%A9%E6%98%8E%E7%A1%AE%E6%8F%90%E5%87%BA%E2%80%9C%E6%8C%AF%E5%85%B4%E4%B8%AD%E5%8D%8E%E2%80%9D%E5%8F%A3%E5%8F%B7%E7%9A%84%E6%98%AF%EF%BC%9A\n" + \
                       "c0-e346=number:9\n" + \
                       "c0-e347=null:null\n" + \
                       "c0-e348=null:null\n" + \
                       "c0-e349=number:2\n" + \
                       "c0-e350=null:null\n" + \
                       "c0-e351=null:null\n" + \
                       "c0-e352=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E4%B8%AD%E5%9B%BD%E8%BF%91%E4%BB%A3%E6%9C%80%E6%97%A9%E6%98%8E%E7%A1%AE%E6%8F%90%E5%87%BA%E2%80%9C%E6%8C%AF%E5%85%B4%E4%B8%AD%E5%8D%8E%E2%80%9D%E5%8F%A3%E5%8F%B7%E7%9A%84%E6%98%AF%EF%BC%9A%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e353=null:null\n" + \
                       "c0-e354=null:null\n" + \
                       "c0-e355=number:1\n" + \
                       "c0-e306=Object_Object:{allowUpload:reference:c0-e307,analyse:reference:c0-e308,description:reference:c0-e309,fillblankType:reference:c0-e310,gmtCreate:reference:c0-e311,gmtModified:reference:c0-e312,id:reference:c0-e313,judgeDtos:reference:c0-e314,judgerules:reference:c0-e315,ojCases:reference:c0-e316,ojMemLimit:reference:c0-e317,ojNeedInput:reference:c0-e318,ojSupportedLanguage:reference:c0-e319,ojSupportedLanguageList:reference:c0-e320,ojTimeLimit:reference:c0-e321,ojTryTime:reference:c0-e322,optionDtos:reference:c0-e323,options:reference:c0-e344,plainTextTitle:reference:c0-e345,position:reference:c0-e346,sampleAnswerJson:reference:c0-e347,sampleAnswers:reference:c0-e348,score:reference:c0-e349,stdAnswer:reference:c0-e350,testId:reference:c0-e351,title:reference:c0-e352,titleAttachment:reference:c0-e353,titleAttachmentDtos:reference:c0-e354,type:reference:c0-e355}\n" + \
                       "c0-e357=null:null\n" + \
                       "c0-e358=null:null\n" + \
                       "c0-e359=null:null\n" + \
                       "c0-e360=null:null\n" + \
                       "c0-e361=null:null\n" + \
                       "c0-e362=null:null\n" + \
                       "c0-e363=number:1235777994\n" + \
                       "c0-e364=null:null\n" + \
                       "c0-e365=null:null\n" + \
                       "c0-e366=null:null\n" + \
                       "c0-e367=null:null\n" + \
                       "c0-e368=null:null\n" + \
                       "c0-e369=null:null\n" + \
                       "c0-e370=null:null\n" + \
                       "c0-e371=null:null\n" + \
                       "c0-e372=null:null\n" + \
                       "c0-e375=null:null\n" + \
                       "c0-e376=null:null\n" + \
                       "c0-e377=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E5%8E%86%E5%8F%B2%E5%92%8C%E4%BA%BA%E6%B0%91%E9%80%89%E6%8B%A9%E4%BA%86%E6%94%B9%E9%9D%A9%E5%BC%80%E6%94%BE%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e378=number:465063877014476\n" + \
                       "c0-e374=Object_Object:{analyse:reference:c0-e375,answer:reference:c0-e376,content:reference:c0-e377,id:reference:c0-e378}\n" + \
                       "c0-e380=null:null\n" + \
                       "c0-e381=null:null\n" + \
                       "c0-e382=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E5%8E%86%E5%8F%B2%E5%92%8C%E4%BA%BA%E6%B0%91%E9%80%89%E6%8B%A9%E4%BA%86%E4%B8%AD%E5%9B%BD%E5%85%B1%E4%BA%A7%E5%85%9A%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e383=number:165063877014476\n" + \
                       "c0-e379=Object_Object:{analyse:reference:c0-e380,answer:reference:c0-e381,content:reference:c0-e382,id:reference:c0-e383}\n" + \
                       "c0-e385=null:null\n" + \
                       "c0-e386=null:null\n" + \
                       "c0-e387=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E5%8E%86%E5%8F%B2%E5%92%8C%E4%BA%BA%E6%B0%91%E9%80%89%E6%8B%A9%E4%BA%86%E7%A4%BE%E4%BC%9A%E4%B8%BB%E4%B9%89%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e388=number:265063877014476\n" + \
                       "c0-e384=Object_Object:{analyse:reference:c0-e385,answer:reference:c0-e386,content:reference:c0-e387,id:reference:c0-e388}\n" + \
                       "c0-e390=null:null\n" + \
                       "c0-e391=null:null\n" + \
                       "c0-e392=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E5%8E%86%E5%8F%B2%E5%92%8C%E4%BA%BA%E6%B0%91%E9%80%89%E6%8B%A9%E4%BA%86%E4%BA%BA%E6%B0%91%E6%B0%91%E4%B8%BB%E4%B8%93%E6%94%BF%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e393=number:365063877014476\n" + \
                       "c0-e389=Object_Object:{analyse:reference:c0-e390,answer:reference:c0-e391,content:reference:c0-e392,id:reference:c0-e393}\n" + \
                       "c0-e373=Array:[reference:c0-e374,reference:c0-e379,reference:c0-e384,reference:c0-e389]\n" + \
                       "c0-e394=null:null\n" + \
                       "c0-e395=string:%E4%B8%8B%E5%88%97%E9%80%89%E9%A1%B9%E4%B8%AD%E5%B1%9E%E4%BA%8E%E2%80%9C%E5%9B%9B%E4%B8%AA%E9%80%89%E6%8B%A9%E2%80%9D%E7%9A%84%E6%9C%89%EF%BC%9A\n" + \
                       "c0-e396=number:10\n" + \
                       "c0-e397=null:null\n" + \
                       "c0-e398=null:null\n" + \
                       "c0-e399=number:3\n" + \
                       "c0-e400=null:null\n" + \
                       "c0-e401=null:null\n" + \
                       "c0-e402=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E4%B8%8B%E5%88%97%E9%80%89%E9%A1%B9%E4%B8%AD%E5%B1%9E%E4%BA%8E%E2%80%9C%E5%9B%9B%E4%B8%AA%E9%80%89%E6%8B%A9%E2%80%9D%E7%9A%84%E6%9C%89%EF%BC%9A%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e403=null:null\n" + \
                       "c0-e404=null:null\n" + \
                       "c0-e405=number:2\n" + \
                       "c0-e356=Object_Object:{allowUpload:reference:c0-e357,analyse:reference:c0-e358,description:reference:c0-e359,fillblankType:reference:c0-e360,gmtCreate:reference:c0-e361,gmtModified:reference:c0-e362,id:reference:c0-e363,judgeDtos:reference:c0-e364,judgerules:reference:c0-e365,ojCases:reference:c0-e366,ojMemLimit:reference:c0-e367,ojNeedInput:reference:c0-e368,ojSupportedLanguage:reference:c0-e369,ojSupportedLanguageList:reference:c0-e370,ojTimeLimit:reference:c0-e371,ojTryTime:reference:c0-e372,optionDtos:reference:c0-e373,options:reference:c0-e394,plainTextTitle:reference:c0-e395,position:reference:c0-e396,sampleAnswerJson:reference:c0-e397,sampleAnswers:reference:c0-e398,score:reference:c0-e399,stdAnswer:reference:c0-e400,testId:reference:c0-e401,title:reference:c0-e402,titleAttachment:reference:c0-e403,titleAttachmentDtos:reference:c0-e404,type:reference:c0-e405}\n" + \
                       "c0-e407=null:null\n" + \
                       "c0-e408=null:null\n" + \
                       "c0-e409=null:null\n" + \
                       "c0-e410=null:null\n" + \
                       "c0-e411=null:null\n" + \
                       "c0-e412=null:null\n" + \
                       "c0-e413=number:1235777996\n" + \
                       "c0-e414=null:null\n" + \
                       "c0-e415=null:null\n" + \
                       "c0-e416=null:null\n" + \
                       "c0-e417=null:null\n" + \
                       "c0-e418=null:null\n" + \
                       "c0-e419=null:null\n" + \
                       "c0-e420=null:null\n" + \
                       "c0-e421=null:null\n" + \
                       "c0-e422=null:null\n" + \
                       "c0-e425=null:null\n" + \
                       "c0-e426=null:null\n" + \
                       "c0-e427=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E8%BE%9B%E4%BA%A5%E9%9D%A9%E5%91%BD%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e428=number:44593793598617\n" + \
                       "c0-e424=Object_Object:{analyse:reference:c0-e425,answer:reference:c0-e426,content:reference:c0-e427,id:reference:c0-e428}\n" + \
                       "c0-e430=null:null\n" + \
                       "c0-e431=null:null\n" + \
                       "c0-e432=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E5%9B%BD%E6%B0%91%E9%9D%A9%E5%91%BD%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e433=number:144593793598617\n" + \
                       "c0-e429=Object_Object:{analyse:reference:c0-e430,answer:reference:c0-e431,content:reference:c0-e432,id:reference:c0-e433}\n" + \
                       "c0-e435=null:null\n" + \
                       "c0-e436=null:null\n" + \
                       "c0-e437=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2016px%3B%22%20%20%3E%E6%96%B0%E4%B8%AD%E5%9B%BD%E5%BB%BA%E7%AB%8B%E5%92%8C%E7%A4%BE%E4%BC%9A%E4%B8%BB%E4%B9%89%E5%88%B6%E5%BA%A6%E5%BB%BA%E7%AB%8B%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e438=number:344593793598617\n" + \
                       "c0-e434=Object_Object:{analyse:reference:c0-e435,answer:reference:c0-e436,content:reference:c0-e437,id:reference:c0-e438}\n" + \
                       "c0-e440=null:null\n" + \
                       "c0-e441=null:null\n" + \
                       "c0-e442=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%20text-indent%3A%2016px%3B%22%20%20%3E%E6%94%B9%E9%9D%A9%E5%BC%80%E6%94%BE%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e443=number:444593793598617\n" + \
                       "c0-e439=Object_Object:{analyse:reference:c0-e440,answer:reference:c0-e441,content:reference:c0-e442,id:reference:c0-e443}\n" + \
                       "c0-e423=Array:[reference:c0-e424,reference:c0-e429,reference:c0-e434,reference:c0-e439]\n" + \
                       "c0-e444=null:null\n" + \
                       "c0-e445=string:%E4%B8%8B%E5%88%97%E9%80%89%E9%A1%B9%E4%B8%AD%E5%B1%9E%E4%BA%8E20%E4%B8%96%E7%BA%AA%E4%B8%AD%E5%9B%BD%E4%B8%89%E6%AC%A1%E5%8E%86%E5%8F%B2%E6%80%A7%E5%B7%A8%E5%8F%98%E7%9A%84%E6%9C%89%EF%BC%9A\n" + \
                       "c0-e446=number:12\n" + \
                       "c0-e447=null:null\n" + \
                       "c0-e448=null:null\n" + \
                       "c0-e449=number:3\n" + \
                       "c0-e450=null:null\n" + \
                       "c0-e451=null:null\n" + \
                       "c0-e452=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E4%B8%8B%E5%88%97%E9%80%89%E9%A1%B9%E4%B8%AD%E5%B1%9E%E4%BA%8E20%3C%2Fspan%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E4%B8%96%E7%BA%AA%E4%B8%AD%E5%9B%BD%E4%B8%89%E6%AC%A1%E5%8E%86%E5%8F%B2%E6%80%A7%E5%B7%A8%E5%8F%98%E7%9A%84%E6%9C%89%EF%BC%9A%3C%2Fspan%3E%3C%2Fp%3E%3Cp%3E%3Cbr%20%3E%3C%2Fp%3E\n" + \
                       "c0-e453=null:null\n" + \
                       "c0-e454=null:null\n" + \
                       "c0-e455=number:2\n" + \
                       "c0-e406=Object_Object:{allowUpload:reference:c0-e407,analyse:reference:c0-e408,description:reference:c0-e409,fillblankType:reference:c0-e410,gmtCreate:reference:c0-e411,gmtModified:reference:c0-e412,id:reference:c0-e413,judgeDtos:reference:c0-e414,judgerules:reference:c0-e415,ojCases:reference:c0-e416,ojMemLimit:reference:c0-e417,ojNeedInput:reference:c0-e418,ojSupportedLanguage:reference:c0-e419,ojSupportedLanguageList:reference:c0-e420,ojTimeLimit:reference:c0-e421,ojTryTime:reference:c0-e422,optionDtos:reference:c0-e423,options:reference:c0-e444,plainTextTitle:reference:c0-e445,position:reference:c0-e446,sampleAnswerJson:reference:c0-e447,sampleAnswers:reference:c0-e448,score:reference:c0-e449,stdAnswer:reference:c0-e450,testId:reference:c0-e451,title:reference:c0-e452,titleAttachment:reference:c0-e453,titleAttachmentDtos:reference:c0-e454,type:reference:c0-e455}\n" + \
                       "c0-e457=null:null\n" + \
                       "c0-e458=null:null\n" + \
                       "c0-e459=null:null\n" + \
                       "c0-e460=null:null\n" + \
                       "c0-e461=null:null\n" + \
                       "c0-e462=null:null\n" + \
                       "c0-e463=number:1235777997\n" + \
                       "c0-e464=null:null\n" + \
                       "c0-e465=null:null\n" + \
                       "c0-e466=null:null\n" + \
                       "c0-e467=null:null\n" + \
                       "c0-e468=null:null\n" + \
                       "c0-e469=null:null\n" + \
                       "c0-e470=null:null\n" + \
                       "c0-e471=null:null\n" + \
                       "c0-e472=null:null\n" + \
                       "c0-e475=null:null\n" + \
                       "c0-e476=null:null\n" + \
                       "c0-e477=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E7%B2%BE%E7%A5%9E%E6%96%87%E6%98%8E%E7%9A%84%E7%8E%B0%E4%BB%A3%E5%8C%96%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e478=number:444593860978670\n" + \
                       "c0-e474=Object_Object:{analyse:reference:c0-e475,answer:reference:c0-e476,content:reference:c0-e477,id:reference:c0-e478}\n" + \
                       "c0-e480=null:null\n" + \
                       "c0-e481=null:null\n" + \
                       "c0-e482=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E7%94%9F%E6%80%81%E6%96%87%E6%98%8E%E7%9A%84%E7%8E%B0%E4%BB%A3%E5%8C%96%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e483=number:344593860978670\n" + \
                       "c0-e479=Object_Object:{analyse:reference:c0-e480,answer:reference:c0-e481,content:reference:c0-e482,id:reference:c0-e483}\n" + \
                       "c0-e485=null:null\n" + \
                       "c0-e486=null:null\n" + \
                       "c0-e487=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E5%88%B6%E5%BA%A6%E6%96%87%E5%8C%96%E7%9A%84%E7%8E%B0%E4%BB%A3%E5%8C%96%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e488=number:144593860978670\n" + \
                       "c0-e484=Object_Object:{analyse:reference:c0-e485,answer:reference:c0-e486,content:reference:c0-e487,id:reference:c0-e488}\n" + \
                       "c0-e490=null:null\n" + \
                       "c0-e491=null:null\n" + \
                       "c0-e492=string:%3Cp%3E%3Cspan%20style%3D%22font-family%3A%20%E5%AE%8B%E4%BD%93%3B%20font-size%3A%2016px%3B%22%20%20%3E%E7%89%A9%E8%B4%A8%E6%96%87%E6%98%8E%E7%9A%84%E7%8E%B0%E4%BB%A3%E5%8C%96%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e493=number:44593860978670\n" + \
                       "c0-e489=Object_Object:{analyse:reference:c0-e490,answer:reference:c0-e491,content:reference:c0-e492,id:reference:c0-e493}\n" + \
                       "c0-e473=Array:[reference:c0-e474,reference:c0-e479,reference:c0-e484,reference:c0-e489]\n" + \
                       "c0-e494=null:null\n" + \
                       "c0-e495=string:%E8%BF%91%E4%BB%A3%E4%B8%AD%E5%9B%BD%E7%9A%84%E7%8E%B0%E4%BB%A3%E5%8C%96%E4%B8%BB%E8%A6%81%E6%98%AF%E6%8C%87%EF%BC%9A\n" + \
                       "c0-e496=number:13\n" + \
                       "c0-e497=null:null\n" + \
                       "c0-e498=null:null\n" + \
                       "c0-e499=number:3\n" + \
                       "c0-e500=null:null\n" + \
                       "c0-e501=null:null\n" + \
                       "c0-e502=string:%3Cp%20style%3D%22line-height%3A%20150%25%3B%22%20%20%3E%3Cspan%20style%3D%22font-size%3A16px%3Bline-height%3A150%25%3Bfont-family%3A%E5%AE%8B%E4%BD%93%3B%22%20%20%3E%E8%BF%91%E4%BB%A3%E4%B8%AD%E5%9B%BD%E7%9A%84%E7%8E%B0%E4%BB%A3%E5%8C%96%E4%B8%BB%E8%A6%81%E6%98%AF%E6%8C%87%EF%BC%9A%3C%2Fspan%3E%3C%2Fp%3E\n" + \
                       "c0-e503=null:null\n" + \
                       "c0-e504=null:null\n" + \
                       "c0-e505=number:2\n" + \
                       "c0-e456=Object_Object:{allowUpload:reference:c0-e457,analyse:reference:c0-e458,description:reference:c0-e459,fillblankType:reference:c0-e460,gmtCreate:reference:c0-e461,gmtModified:reference:c0-e462,id:reference:c0-e463,judgeDtos:reference:c0-e464,judgerules:reference:c0-e465,ojCases:reference:c0-e466,ojMemLimit:reference:c0-e467,ojNeedInput:reference:c0-e468,ojSupportedLanguage:reference:c0-e469,ojSupportedLanguageList:reference:c0-e470,ojTimeLimit:reference:c0-e471,ojTryTime:reference:c0-e472,optionDtos:reference:c0-e473,options:reference:c0-e494,plainTextTitle:reference:c0-e495,position:reference:c0-e496,sampleAnswerJson:reference:c0-e497,sampleAnswers:reference:c0-e498,score:reference:c0-e499,stdAnswer:reference:c0-e500,testId:reference:c0-e501,title:reference:c0-e502,titleAttachment:reference:c0-e503,titleAttachmentDtos:reference:c0-e504,type:reference:c0-e505}\n" + \
                       "c0-e5=Array:[reference:c0-e6,reference:c0-e56,reference:c0-e106,reference:c0-e156,reference:c0-e206,reference:c0-e256,reference:c0-e306,reference:c0-e356,reference:c0-e406,reference:c0-e456]\n" + \
                       "c0-e506=boolean:true\n" + \
                       "c0-e507=Array:[]\n" + \
                       "c0-e508=number:1\n" + \
                       "c0-e509=number:1224360494\n" + \
                       "c0-e510=string:%E7%BB%AA%E8%AE%BA%E5%8D%95%E5%85%83%E6%B5%8B%E8%AF%95\n" + \
                       "c0-e511=number:2\n" + \
                       "c0-param0=Object_Object:{aid:reference:c0-e1,answers:reference:c0-e2,autoSubmit:reference:c0-e3,evaluateVo:reference:c0-e4,objectiveQList:reference:c0-e5,showAnalysis:reference:c0-e506,subjectiveQList:reference:c0-e507,submitStatus:reference:c0-e508,tid:reference:c0-e509,tname:reference:c0-e510,type:reference:c0-e511}\n" + \
                       "c0-param1=boolean:false\n" + \
                       "batchId=1"
        url = self.base_url + "/dwr/call/plaincall/MocQuizBean.submitAnswers.dwr"
        requests.packages.urllib3.disable_warnings()
        requests.post(url=url, headers=self.headers, cookies=self.cookies, verify=False, data=request_data)

    # 返回当前已经发布的章节号chapter_number
    def get_learned_term_dto(self, tid='1450773590'):
        request_data = "callCount=1\n" \
                       "scriptSessionId=${scriptSessionId}190\n" \
                       "httpSessionId=40219d8c4ef84a0d9ba9e1c4ea95d0c5\n" \
                       "c0-scriptName=CourseBean\n" \
                       "c0-methodName=getLastLearnedMocTermDto\n" \
                       "c0-id=0\n" + \
                       "c0-param0=number:" + tid + "\n" + \
                       "batchId=1583654271813"
        requests.packages.urllib3.disable_warnings()
        url = self.base_url + "/dwr/call/plaincall/CourseBean.getLastLearnedMocTermDto.dwr"
        res = requests.post(url=url, headers=self.headers, cookies=self.cookies, verify=False, data=request_data)
        res.encoding = 'unicode_escape'
        text = Util.remove_label_and_callback(res.text)
        # 去掉jsonContent字段
        text = re.sub('s[0-9]+\.jsonContent=(("(\[|{).*?(\]|})";)|(null;))', '', text)
        # 去掉isTestChecked和name连起来的字段
        text = re.sub('s[0-9]+\.liveInfoDto.*name=.*";', '', text)
        js = execjs.compile(text)

        chapter_number_list = []
        dict = js.eval('s0')
        for chapter in dict['chapters']:
            # chapter['name']
            for quiz in chapter['quizs']:
                # print(quiz['contentId'])
                if quiz['contentId'] is not None or len(quiz['contentId']) != 0:
                    chapter_number_list.append(str(quiz['contentId']))

        print("当前已有章节号：" + str(chapter_number_list))
        return chapter_number_list

    # 获取自己已做过的测验集
    def get_all_learned_quiz_list(self, tid='1450773590'):
        quiz_list = []
        chapter_number_list = self.get_learned_term_dto(tid)
        for chapter_number in chapter_number_list:
            quiz_number_list = self.get_quiz_info(chapter_number)
            for quiz_number in quiz_number_list:
                quiz_list_part = self.get_quiz_paper_dto(chapter_number, quiz_number)
                # self.save_all_quiz(quiz_list)
                quiz_list.extend(quiz_list_part)
        return quiz_list

    # 保存所有的测验到数据库
    @staticmethod
    def save_all_quiz(self, quiz_list):
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        db = client['tmp']
        exercise_collection = db['exercise']
        for quiz in quiz_list:
            # print(quiz)
            result = exercise_collection.find({"id": quiz['id']})
            if result.count() == 0:
                exercise_collection.insert_one(quiz)
                print("新增题目：" + str(quiz))
            # 集合中已存在该文档
            else:
                for option in quiz['optionDtos']:
                    exercise_collection.update_one({"id": quiz["id"]}, {"$addToSet": {"optionDtos": option}})

                    # if result.count() == 0:
                    #     print("新增选项：" + str(option))
                    #     exercise_collection.update_one(dict, {"$addToSet": {"optionDtos": option}})
            # print(quiz['id'])
            # exercise_collection.update_one()

    # 测试，获取chapter_number，再根据chapter_number去获取quiz_number，提交后获取quiz_list查看是否正确
    def test(self):
        chapter_number_list = self.get_learned_term_dto()
        chapter_number = chapter_number_list[0]
        quiz_number = self.get_new_quiz_number(chapter_number)
        print("当前新的测验号：" + quiz_number)
        self.submit_quiz_answer(quiz_number)


if __name__ == '__main__':
    spider = MoocSpider()

    # 获取已做过的测验列表并保存该列表到数据库
    # quiz_list = spider.get_all_learned_quiz_list()
    # spider.save_all_quiz(quiz_list)

    spider.test()
