# MoocSpider

写这个爬虫的初心，是希望能够把mooc上的题目放到自己的flashcard模版里，为了能够更好的掌握和记忆知识，尽管有一个自己的题库可以更好更方便的应付考试，但我还是想靠自己去完成。

本人技拙，因为分析mooc并且写这个爬虫，导致了两次网课都忘记完成……希望接下来的时间里靠我自己的大脑弥补损失，抵制通过题库搜题过考试的行为。

接下来是一些程序相关的内容：

## Preview
![爬虫运行截图](https://upload-images.jianshu.io/upload_images/14611955-fe576017a17544e1.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![单选题](https://upload-images.jianshu.io/upload_images/14611955-10f9c2d0e60b5ede.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![多选题](https://upload-images.jianshu.io/upload_images/14611955-13cf2c1390715deb.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![填空题](https://upload-images.jianshu.io/upload_images/14611955-602fdf4125bffe09.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![判断题](https://upload-images.jianshu.io/upload_images/14611955-87b4cbe7083ced9d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

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
![PicGo_Preview](https://upload-images.jianshu.io/upload_images/14611955-d6485d0cd2f4f2fe.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### 目录树生成工具使用的是directory-tree-generator（忘了项目地址了）
![directory-tree-generator_Preview](https://upload-images.jianshu.io/upload_images/14611955-f0eb6ff312541498.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)