class Option(object):
    def __init__(self, content='', answer=False):
        self.content = content
        self.answer = answer


class Exercise(object):
    def __init__(self, title=''):
        self.title = title
        self.options = []

    def __str__(self):
        string = "题目：" + self.title + "\n"
        for option in self.options:
            string = string + option.content + " isAnswer? " + str(option.answer) + "\n"
        string = string + "============================================================================================"
        return string
