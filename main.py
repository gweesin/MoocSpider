import requests
import re
import pprint
from exercise import Exercise, Option
import execjs
import pymongo
from util import Util
from urllib.parse import quote


class MoocSpider(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Content-Type": "text/plain",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Origin": "https://www.icourse163.org",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
        }
        self.cookies = {'EDUWEBDEVICE': '23398d07cfdc49f5899ea09bd954c4a5',
                        '__yadk_uid': '0afu1UBllLbDlkqVW1yclfu1NBqJHZld',
                        'NTES_YD_PASSPORT': 'Xll0WPvmB7y1H.zIr7oe.5skYDVUgrW0i2TDxLcAVLfVwsISwc4gjpUhAmaTEQkLeErFUQ7Qkta2oyWvWpnUERWUG2rVGtJ8evPAeglAwRPVozmTdFz0Ie5EgVjuxg0rBKfpT24LRktBrgcoyykMphgVhZ7YadJ6Q_9YM1i7s4R6EuvJtmg5L.Fbq9sz..dH9oSmLsESBxYQ97iOxgf0xwS_3',
                        'P_INFO': '15959782573|1583414964|1|imooc|00&99|null&null&null#fuj&null#10#0|&0||15959782573',
                        'hasVolume': 'true',
                        'videoResolutionType': '3',
                        'videoRate': '1.75',
                        'videoVolume': '1',
                        'NTESSTUDYSI': '40219d8c4ef84a0d9ba9e1c4ea95d0c5',
                        'NETEASE_WDA_UID': '1385959575#|#1551620478949',
                        'WM_TID': 'XP1IV3hOpYlAAUVAAEZqQYiM6FnHbq2X',
                        'STUDY_INFO': '"yd.981f1ed17b924e66a@163.com|8|1385959575|1583815069081"',
                        'STUDY_SESS': '"2rYknfJqYdqYWXFIQIb3Cu4QcTZsfFYTKzEyH7Trrt7ybOgVMLblMZA56Vg55h0T2LvsqemS6Xmwq8f+sUJGLcfkAFFc4EvWN1Pcw5KxzlJlCYuCH1Mc6bhCkXosygOdBJQqIBL6E8c7U8UDJYedwxISR8LrRlcJaaG9LLLxwOALhur2Nm2wEb9HcEikV+3FTI8+lZKyHhiycNQo+g+/oA=="',
                        'STUDY_PERSIST': '"Fclw9gZwcMNzEHNwOku/LzO4qf0vOBFVDiuIeL9UjPHRsUmIkCeL+eHTqyymsoS56SvXk+OASJ3PascNlawo+buFqWCG8+PBbtxfewuiwauzhrfrwb9av4XatgA7JVlAzEvGuFLl4ufG/K02hte9PwmRhS5fDkdkj4CtbEalxV3mTJX7LWJtgiQ4efIK66jx/VCeTqld6D+++eSS9mp8Vto49BD0TJbflUp9f/kiFdvZgpjCC7Iso4RP9U87vJE8LtaQzUT1ovP2MqtW5+L3Hw+PvH8+tZRDonbf7gEH7JU="',
                        'WM_NI': 'bAzfttJtDs552ThyOfpcj2v2pbnUkskT1FLyqclRb5BzHdjuA1NmsW9AOBpRri3MLm3eg9V8BCUby1WM1hiAfse8H34xNktwEUv8luHxaIZPMHCAPcXXlEW8CwqQLoTiN0k%3D',
                        'WM_NIKE': '9ca17ae2e6ffcda170e2e6eebbeb68a5988298ea66f3a88bb6c85f829e8ebbf55aa38ffd88e980f697b6b8f82af0fea7c3b92aa29fb687f7808aac8c94b83ff28ca89ace6eb4bda6d3f53ab4bea2b6ea79a98cffa7cf73b3bda4b3e13f82a68885e97f83ef828ef25dfb9f81a3f35ab2b7fdaecf67f1bba9dad534829d9b83fc3b9593ff89ec4ba6adabd9cb39f8a8828cf77d878bbad9ef7f8ca8afaad95c8f988da2d3699c88a4a6d63481a9bfb2cf6598b782d1ea37e2a3', }
        self.base_url = "https://www.icourse163.org"

    def get_quiz_paper_dto(self, chapter_number, quiz_number):
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
        # print(res.text)
        quiz_number = Util.get_attr_value("aid", res.text)
        return (quiz_number, res.text, chapter_number)

    # 获取具体chapter_number已做过的quiz_number列表
    def get_quiz_info(self, chapter_number):
        request_data = "callCount=1\n" \
                       "scriptSessionId=${scriptSessionId}190\n" \
                       "httpSessionId=40219d8c4ef84a0d9ba9e1c4ea95d0c5\n" \
                       "c0-scriptName=MocQuizBean\n" \
                       "c0-methodName=getQuizInfo\n" \
                       "c0-id=0\n" \
                       "c0-param0=number:" + chapter_number + "\n" + \
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
    def submit_quiz_answer(self, quiz_number, text, chapter_number):
        """
        提交会返回错误的response，但是必须提交；
        后台有检测机制，如果没提交，下次申请的还是同一份测验题目，
        应该是为了让用户在断网重连之后，还能继续做同一份题
        """
        query_number = Util.get_attr_value('objectiveQList', text)
        text = Util.remove_label_and_callback(text)
        # text = Util.convert_inner_label(text)
        js = execjs.compile(text)
        quiz_list = js.eval(query_number)
        request_data = "callCount=1\n" + \
                       "scriptSessionId=${scriptSessionId}190\n" + \
                       "httpSessionId=40219d8c4ef84a0d9ba9e1c4ea95d0c5\n" + \
                       "c0-scriptName=MocQuizBean\n" + \
                       "c0-methodName=submitAnswers\n" + \
                       "c0-id=0\n" + \
                       "c0-e1=number:" + quiz_number + "\n" + \
                       "c0-e2=null:null\n" + \
                       "c0-e3=boolean:false\n" + \
                       "c0-e4=null:null\n"
        request_data += Util.convert2req(quiz_list, chapter_number)
        # request_data = quote(request_data, encoding='utf-8')
        # print(request_data)

        url = self.base_url + "/dwr/call/plaincall/MocQuizBean.submitAnswers.dwr"
        requests.packages.urllib3.disable_warnings()
        requests.post(url=url, headers=self.headers, cookies=self.cookies, verify=False,
                      data=request_data.encode('utf-8'))

    # 返回当前已经发布的章节号chapter_number
    def get_learned_term_dto(self, tid):
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
    def get_all_learned_quiz_list(self, tid, collection_name):
        quiz_list = []
        chapter_number_list = self.get_learned_term_dto(tid)
        for chapter_number in chapter_number_list:
            quiz_number_list = self.get_quiz_info(chapter_number)
            for quiz_number in quiz_number_list:
                quiz_list_part = self.get_quiz_paper_dto(chapter_number, quiz_number)
                # self.save_all_quiz(quiz_list)
                quiz_list.extend(quiz_list_part)
        # return quiz_list
        self.save_all_quiz(quiz_list, collection_name)

    # 批量获取所有章节新生成的测验集，每章获取cnt次
    def get_new_quiz_list(self, tid, cnt=5, collection_name='test'):
        chapter_number_list = self.get_learned_term_dto(tid)
        quiz_list = []
        for chapter_number in chapter_number_list:
            for cur_cnt in range(cnt):
                quiz_number, text, chapter_number = self.get_new_quiz_number(chapter_number)
                print("当前新的测验号：" + quiz_number)
                self.submit_quiz_answer(quiz_number, text, chapter_number)
                temp_quiz_list = self.get_quiz_paper_dto(chapter_number=chapter_number, quiz_number=quiz_number)
                quiz_list.extend(temp_quiz_list)
                # print(quiz_list)
                # self.save_all_quiz(quiz_list)
        self.save_all_quiz(quiz_list, collection_name)

    # 保存所有的测验到数据库
    def save_all_quiz(self, quiz_list, collection_name):
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        db = client['tmp']
        exercise_collection = db[collection_name]
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
        quiz_list = self.get_quiz_paper_dto(chapter_number=chapter_number, quiz_number=quiz_number)
        print(quiz_list)


if __name__ == '__main__':
    spider = MoocSpider()

    # 获取已做过的测验列表并保存该列表到数据库
    # quiz_list = spider.get_all_learned_quiz_list()
    # spider.save_all_quiz(quiz_list)

    # spider.test()
    spider.get_new_quiz_list(tid='1450773590', collection_name="history", cnt=1)
    # spider.get_all_learned_quiz_list(tid='1450773590', collection_name="test2")
    # spider.get_quiz_info('1224360494')

    # quiz_number, text, chapter_number = spider.get_new_quiz_number('1224360494')
    # spider.submit_quiz_answer(quiz_number, text, chapter_number)
