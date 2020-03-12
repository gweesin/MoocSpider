# MoocSpider

写这个爬虫的初心，是希望能够把mooc上的题目放到自己的flashcard模版里，为了能够更好的掌握和记忆知识，尽管有一个自己的题库可以更好更方便的应付考试，但我还是想靠自己去完成。

本人技拙，因为分析mooc并且写这个爬虫，导致了两次网课都忘记完成……希望接下来的时间里靠我自己的大脑弥补损失，抵制通过题库搜题过考试的行为。

接下来是一些程序相关的内容：

## Preview
![爬虫运行截图](http://q5xvt6pje.bkt.clouddn.com/picGo/20200312230624.png)
![单选题](http://q5xvt6pje.bkt.clouddn.com/picGo/20200312231309.png)
![多选题](http://q5xvt6pje.bkt.clouddn.com/picGo/20200312232107.png)
![填空题](http://q5xvt6pje.bkt.clouddn.com/picGo/20200312232149.png)
![判断题](http://q5xvt6pje.bkt.clouddn.com/picGo/20200312232228.png)

## DirectoryTree
```text
├─ convertData2Csv.py # Dict转CSV
├─ cookie.py # Cookie异常类
├─ cookie.txt # Cookies字符串读取文件
├─ exercise.py # 目前已无用
├─ main.py # 爬虫
├─ quiz.csv # 生成的csv文件
├─ README.md
├─ util.py # 工具类，诸如cookie字符串转为dict之类的功能
└─ __pycache__
	├─ cookie.cpython-37.pyc
	├─ exercise.cpython-37.pyc
	└─ util.cpython-37.pyc
```

## PS

### 图片上传图床工具使用的是PicGo
![PicGo_Preview](http://q5xvt6pje.bkt.clouddn.com/picGo/20200312233016.png)

### 目录树生成工具使用的是directory-tree-generator（忘了项目地址了）
![directory-tree-generator_Preview](http://q5xvt6pje.bkt.clouddn.com/picGo/20200312233307.png)
