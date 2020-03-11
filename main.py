import requests
import re
import execjs
import pymongo
from util import Util
from cookie import CookieOverdueError
from pprint import pprint

quiz_count = 0


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
        self.cookies = Util.get_cookie_dict()
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
                       "httpSessionId=%s\n" % self.cookies['NTESSTUDYSI'] + \
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
        # 替换html空格"&nbsp;"为" "
        text = Util.convert_html_blankspace(text)
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
                       "httpSessionId=%s\n" % self.cookies['NTESSTUDYSI'] + \
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
                       "httpSessionId=%s\n" % self.cookies['NTESSTUDYSI'] + \
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
                       "httpSessionId=%s\n" % self.cookies['NTESSTUDYSI'] + \
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
        res = requests.post(url=url, headers=self.headers, cookies=self.cookies, verify=False,
                            data=request_data.encode('utf-8'))

        if re.search('not_auth', res.text) is not None:
            raise CookieOverdueError('Cookie信息无效或过期！请重新获取Cookie后再试')

    # 返回当前已经发布的章节号chapter_number
    def get_learned_term_dto(self, tid):
        request_data = "callCount=1\n" \
                       "scriptSessionId=${scriptSessionId}190\n" \
                       "httpSessionId=%s\n" % self.cookies['NTESSTUDYSI'] + \
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
        global quiz_count

        try:
            chapter_number_list = self.get_learned_term_dto(tid)
            # quiz_list = []
            for chapter_number in chapter_number_list:
                for cur_cnt in range(cnt):
                    quiz_number, text, chapter_number = self.get_new_quiz_number(chapter_number)
                    # print("当前新的测验号：" + quiz_number)
                    self.submit_quiz_answer(quiz_number, text, chapter_number)
                    temp_quiz_list = self.get_quiz_paper_dto(chapter_number=chapter_number, quiz_number=quiz_number)
                    # quiz_list.extend(temp_quiz_list)
                    self.save_all_quiz(temp_quiz_list, collection_name)
            # self.save_all_quiz(quiz_list, collection_name)
        except CookieOverdueError as e:
            print(e)
            return
        finally:
            print("本次共新增" + str(quiz_count) + "道题目")

    # 保存所有的测验到数据库
    def save_all_quiz(self, quiz_list, collection_name):
        global quiz_count

        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        db = client['tmp']
        exercise_collection = db[collection_name]
        for quiz in quiz_list:
            """count is deprecated. Use Collection.count_documents instead.
            result = exercise_collection.find({"id": quiz['id']})
            if result.count() == 0:
            """
            if exercise_collection.count_documents({"id": quiz['id']}) == 0:
                exercise_collection.insert_one(quiz)
                quiz_count += 1
                print("新增题目：" + quiz['title'])
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

    def test_judge(self):
        # text =self.get_quiz_info('')
        quiz_list = self.get_quiz_paper_dto('1220933426', '1671007785')

        pprint(quiz_list)


if __name__ == '__main__':
    spider = MoocSpider()

    # 获取已做过的测验列表并保存该列表到数据库
    # quiz_list = spider.get_all_learned_quiz_list()
    # spider.save_all_quiz(quiz_list)

    # 武大近代史
    # spider.get_new_quiz_list(tid='1450259448', collection_name="history", cnt=10)

    # 青岛大学软件构造
    spider.get_new_quiz_list(tid='1206820205', collection_name="software", cnt=30)

    # spider.test_judge()
    # spider.get_new_quiz_list(tid='1450259448', collection_name="ttt", cnt=10)
