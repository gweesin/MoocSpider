import requests
import re
import pprint
from exercise import Exercise, Option
import pprint
import execjs
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

    # 获取测验页面上的题目、选项和答案
    def get_quiz_paper_dto(self, chapter_number='1224360494', quiz_number='1582379290', exercise_list=[]):
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

        text = Util.remove_label_and_callback(res.text)

        js = execjs.compile(text)
        pprint.pprint(js.eval('s1'))

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

    # 获取具体单元的quiz_number列表
    def get_quiz_info(self, chapter_number='1224360494'):
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
        quiz_number = []
        for x in temp_quiz_number:
            if x not in quiz_number:
                quiz_number.append(x)
        print("做过的测验题号：" + str(quiz_number))
        return quiz_number

    def get_term_dto(self, tid='1450773590'):
        pass


if __name__ == '__main__':
    spider = MoocSpider()
    quiz_number_list = spider.get_quiz_info()
    exercise_list = []
    for quiz_number in quiz_number_list:
        spider.get_quiz_paper_dto(quiz_number=quiz_number,exercise_list=exercise_list)

    # spider.get_quiz_info()
