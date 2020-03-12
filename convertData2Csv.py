import pymongo
import pprint
import csv

"""
把MongoDB的BSON转化为ANKI支持的CSV文件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
因为需要对数据进行二次处理，所以mongoexport不能满足需求

document字段解析：
    type:
        1: 单选
        2: 多选
        3: 填空
        4. 判断
        ps:: 除了填空题的答案在字段“stdAnswer”，其它答案都在“optionDtos”以json对象形式呈现
"""


class MyDb(object):
    def __init__(self, db, collection):
        self.client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        self.db = self.client[db]
        self.collection = self.db[collection]
        self.documents = self.get_documents()

    def get_documents(self):
        documents = self.collection.find()
        return documents

    def __str__(self):
        for document in self.documents:
            pprint.pprint(document)
        return ''

    def convert2csv(self):
        # 26个字母数组序列，表示答案
        alpha_list = [chr(alpha) for alpha in range(ord('A'), ord('A') + 26)]
        # csv文件头
        fields_name = ['id', 'title', 'answer', 'options', 'type']

        with open("quiz.csv", "w+", encoding="utf-8", newline='') as f:
            dict_write = csv.DictWriter(f, fields_name)

            for document in self.documents:
                # 初始化dict，每次循环把dict加入csv文件中
                dict = {
                    'id': document['id'],
                    'title': document['title'],
                    'options': '',
                    'answer': '',
                    'type': document['type']
                }
                if dict['type'] is 3:
                    dict['options'] = document['stdAnswer']
                else:
                    answer_str = ''

                    index = 0
                    for option in document['optionDtos']:
                        dict['options'] += option['content'] + '\n'
                        if option['answer'] is True:
                            answer_str += alpha_list[index]
                        index += 1
                    dict['answer'] = answer_str
                # print(dict)
                dict_write.writerow(dict)


if __name__ == '__main__':
    my_db = MyDb('tmp', 'history')
    # print(my_db)
    my_db.convert2csv()
