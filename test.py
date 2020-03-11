import requests
import execjs


url = "https://mc.stu.126.net/pub/s/core_90dbcd54f5c19f62b8c84cd05aaa0568.js"
requests.packages.urllib3.disable_warnings()

res = requests.get(url=url, verify=False)

# print(res.text)
js = execjs.compile(res.text)

js.call("EDU")