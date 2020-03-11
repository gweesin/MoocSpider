import execjs
import pymongo

"""
content = execjs.compile(
    
        a = {
            "answer":false,
            "tmp":{
                "answer": true
            }
        }
    
)

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
db = client['tmp']
collection = db['test']

collection.insert_one(content.eval('a'))
print(content.eval('a'))
"""

l = ["5"]

d = {
    "hello":2,
    "word":3
}
l.append(d["hello"])
print(l)
d['hello'] = 5
print(l)