import re
import pprint


class CookieOverdueError(Exception):
    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return '\033[1;35;0m' + str(self.arg) + '\033[0m'


def get_cookie_dict():
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
            # print("'" + tmp[0] + "':'" + tmp[1] + '\',')
        print("当前Cookie：")
        pprint.pprint(dict)
        return dict


if __name__ == '__main__':
    get_cookie_dict()
