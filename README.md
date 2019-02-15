# 用Scrapy实现一个爬虫程序

## Scrapy框架
Scrapy是我今天浏览网页的时候看到有人提到才知道，很早之前就想尝试做一个爬虫工具，刚好拿来用一下。如果自己写很难避免去实现html请求，dom分析，输出数据这些操作，无异于制造轮子。Scrapy解决了这些基础的问题，先写个Demo熟悉一下Scrapy。

## 定一个小目标
Demo的需求尽量简单，以熟悉Scrapy为主。设计一个爬虫程序，抓去某个豆瓣小组帖子中当前页面的回复内容。

## 创建项目
```
scrapy startproject douban

// 根据提示使用模版创建group spider
cd douban
scrapy genspider group group.douban.com
```
执行之后生成了 `douban/douban/spiders/group.py` 文件，打开里面的`parse`方法就是我们需要具体实现爬虫代码的地方。先不着急写代码。

## 用scrapy shell调试
这个命令可以直接在命令行中进行网页分析，查看结果。尝试爬取一个豆瓣小组的帖子
```
scrapy shell https://www.douban.com/group/topic/132914779/
```
返回结果中注意一条信息：
```
[scrapy.core.engine] DEBUG: Crawled (403) <GET https://www.douban.com/group/topic/132914779/> (referer: None)
```
返回403，因为豆瓣做了一些爬虫程序的防范措施，需要加一个参数，来模拟是用浏览器在访问豆瓣。
```
scrapy shell https://www.douban.com/group/topic/132914779/ -s USER_AGENT='Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
```
这时候不出意外，返回值应该是200，成功访问到了页面。同时也进入了python的命令行模拟。我们可以在这里执行一些操作。熟悉一下scrapy的API

用浏览器访问，打开开发者工具，查看各个dom和css名字，根据css访问。
```python
response.css('li.comment-item')
```
打印出了所有的回复帖子的li标签，结果是一个列表。内容太多不列出来了。

接着查看第一个回复的内容，注意`::text`这个是用来过滤html标签，只显示标签内的内容。
```python
>>> response.css('li.comment-item')[0].css('div.content').css('p::text').get()
u'\u60f3\u4e0a\u5206\u5feb\uff0c\u5c31\u8ddf\u670b\u53cb\u7ec4\u961f\u53bb\u5427\u3002\u3002'
```
这里显示的unicode编码，显示中文需要额外处理，编码问题先忽略掉。

## 编写爬虫代码
回到`douban/douban/spiders/group.py`文件，根据刚才的调试，实现爬虫功能。
```python
def parse(self, response):
    for comment in response.css('li.comment-item'):
        yield {
            'content': comment.css('div.content').css('p::text').get(),
        }
```
修改start_urls变量为豆瓣帖子的url
```python
start_urls = ['https://www.douban.com/group/topic/132914779/']
```

## 执行程序
执行group爬虫，输出结果到data.json
```
scrapy crawl group -o data.json
```
和刚才一样返回403，一样需要在`douban/settings.py`设置USER_AGENT来假装是浏览器访问。
```python
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
```
`data.json`中已经有数据了，不过编码有问题，现在解决一下输出的json文件是unicode编码的问题，网上查了一圈，乱七八糟的各种方案。最后还是看官网的文档解决的。在`douban/settings.py`设置
```python
FEED_EXPORT_ENCODING = 'utf-8'
```
再跑一遍程序，查看`data.json`
```json
[
{"content": "想上分快，就跟朋友组队去吧。。"},
{"content": "我还在用上古时期的6p 闪退了几次 我卸载了"},
{"content": "想上分快，就跟朋友组队去吧。。"},
{"content": "我有大号，小号练英雄，打上去为了带朋友而已"},
{"content": " 嗯哼。祝好运～"},
{"content": "你可以，补位啊"},
{"content": "一把2个只会法师2个只会射手还不愿意重开你告诉我该补哪个？"},
{"content": "我也是！！！！ 准备为了打游戏换手机了！！"},
...
]
```
看样子是满足之前定制的需求了，翻页抓取也很简单，找到下一页按钮的url，请求这个url再调用一次parse方法。官网也有例子，这里不多说了。
