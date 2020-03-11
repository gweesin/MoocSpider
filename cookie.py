import re
import pprint

def get_cookie_dict():
    with open("cookie.txt", "r", encoding='utf-8') as f:
        cookies = f.read()
        dict = {}

        # 去空格和换行
        cookies = re.sub(' |\n', '', cookies)

        cookie_list = cookies.split(';')
        # for cookie in cookie_list:
        #     tmp = cookie.split('=')
        #     key = tmp[0]
        #     value = tmp[1]
        #     dict[key] = value
        # pprint.pprint(dict)
        for cookie in cookie_list:
            tmp = cookie.split('=')
            print("'" + tmp[0] + "':'" + tmp[1] + '\',')
if __name__ == '__main__':
    get_cookie_dict()
