import requests
import re
import execjs
import pymongo
from util import Util
from cookie import CookieOverdueError
from pprint import pprint
from colorama import Fore, Back, init

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
        # 替换html转义字符为原字符
        text = Util.convert_html_escape_character(text)
        js = execjs.compile(text)

        query_number = Util.get_attr_value("objectiveQList", res.text)

        quiz_list = js.eval(query_number)
        return quiz_list

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

        quiz_number = None
        try:
            quiz_number = Util.get_attr_value("aid", res.text)
        except IndexError:
            print(quiz_number)
            raise IndexError

        return (quiz_number, res.text, chapter_number)

    def get_quiz_info(self, chapter_number):
        """根据chapter_number获取quiz_number_list

        :param chapter_number:
        :return: quiz_number_list
        """
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

    def submit_quiz_answer(self, quiz_number, text, chapter_number):
        """提交答案

        后台有检测机制，如果没提交，下次申请的还是同一份测验题目，
        应该是为了让用户在断网重连之后，还能继续做同一份题

        :param quiz_number: 测验号
        :param text: 测验数据文本
        :param chapter_number: 测验对应的章节号
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

    def get_learned_term_dto(self, tid):
        """根据tid返回当前已经发布的章节号chapter_number_list

        :param tid: 课程号
        :return: chapter_number_list，章节号列表
        """
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

        # 去除testRandomSetting和testTime |(s[0-9]+\.testTime=[0-9]+;)

        def double_quote(matched):
            tmp_str = matched.group('string')
            prefix = 'testRandomSetting="'
            suffix = '";'
            # tmp_str = tmp_str[len(prefix):len(suffix)]
            tmp_str = re.sub('\\"', '', tmp_str[len(prefix):len(suffix)])
            return prefix + tmp_str + suffix

        # 处理双引号"
        text = re.sub('(?P<string>testRandomSetting=".*?";)', double_quote, text)
        js = execjs.compile(text)

        chapter_number_list = []
        # print(text)
        dict = js.eval('s0')
        for chapter in dict['chapters']:
            # chapter['name']
            for quiz in chapter['quizs']:
                # print(quiz['contentId'])
                if quiz['contentId'] is not None or len(quiz['contentId']) != 0:
                    chapter_number_list.append(str(quiz['contentId']))

        chapter_number_list.sort()
        print(Fore.CYAN + "当前已有章节号：" + str(chapter_number_list))
        return chapter_number_list

    def get_all_learned_quiz_list(self, tid, collection_name):
        """获取自己已做过的测验集，并保存数据库

        :param tid: 课程号
        :param collection_name: 数据库collection名称
        :return: None
        """
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

    def get_new_quiz_list(self, tid, cnt=5, collection_name='test'):
        """批量获取所有章节新生成的测验集，每章获取cnt次，并保存数据库

        :param tid: 课程号
        :param cnt: 抓取次数（每次抽取一定量的题目出来，次数越高需要时间越久，但覆盖面也越广）
        :param collection_name: 数据库collection名称
        :return: None
        """
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
            print(Fore.LIGHTRED_EX + "本次共新增" + str(quiz_count) + "道题目")
            quiz_count = 0

    def save_all_quiz(self, quiz_list, collection_name):
        """保存所有的测验到数据库(带查重)

        :param quiz_list: 测验题目列表
        :param collection_name: 数据库collection集合（默认数据库为tmp）
        :return: None
        """
        global quiz_count

        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        db = client['tmp']
        exercise_collection = db[collection_name]
        for quiz in quiz_list:
            if exercise_collection.count_documents({"title": quiz['title']}) == 0:
                exercise_collection.insert_one(quiz)
                quiz_count += 1
                print(Fore.LIGHTYELLOW_EX + "新增题目：" + quiz['title'])
            # 集合中已存在该文档
            else:
                for option in quiz['optionDtos']:
                    flag = exercise_collection.update_one({"title": quiz["title"]},
                                                          {"$addToSet": {"optionDtos": option}})
                    if flag.modified_count is not 0:
                        print(Fore.YELLOW + "新增选项：" + option['content'])


if __name__ == '__main__':
    spider = MoocSpider()

    init(autoreset=True)  # 自动修复

    # 获取已做过的测验列表并保存该列表到数据库
    # quiz_list = spider.get_all_learned_quiz_list()
    # spider.save_all_quiz(quiz_list)

    # 武大近代史
    spider.get_new_quiz_list(tid='1450259448', collection_name="history", cnt=10)  # 第8次开课
    spider.get_new_quiz_list(tid='1207344201', collection_name="history", cnt=10)  # 第7次开课
    spider.get_new_quiz_list(tid='1206055229', collection_name="history", cnt=30)  # 第6次开课
    spider.get_new_quiz_list(tid='1003351002', collection_name="history", cnt=30)  # 第5次开课
    spider.get_new_quiz_list(tid='1002788015', collection_name="history", cnt=30)  # 第4次开课
    spider.get_new_quiz_list(tid='1002328019', collection_name="history", cnt=30)  # 第3次开课
    spider.get_new_quiz_list(tid='1002035025', collection_name="history", cnt=30)  # 第2次开课
    spider.get_new_quiz_list(tid='1001804009', collection_name="history", cnt=30)  # 第1次开课

    # 青岛大学软件构造(软件设计与体系结构)
    # spider.get_new_quiz_list(tid='1206820205', collection_name="software", cnt=30)  # 第1次开课
    # spider.get_new_quiz_list(tid='1450689459', collection_name="software", cnt=30)  # 第2次开课

    # spider.test_judge()
    # spider.get_new_quiz_list(tid='1450259448', collection_name="ttt", cnt=10)
