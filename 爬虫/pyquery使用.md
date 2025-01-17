#### 初始化
可以使用PyQuery加载xml字符串、lxml文档、本地的html文件或者加载url
```
from pyquery import PyQuery as pq
# url
pq(your_url)  如 http://www.qq.com    默认调用 urllib.模块请求  默认超时60s
doc = pq('https://www.qq.com')
print(doc('title')) # 标题

doc = pq(filename='index.html')  # html文件
doc = pq("<html></html>")   # str
doc = pq(etree.fromstring("<html></html>"))  # lxml

```
#### 获取元素
```
html = '''<div>
    <ul id = 'haha'>
         <li class="item-0">first item</li>
         <li class="item-1"><a href="link2.html">second item</a></li>
         <li class="item-0 active"><a href="link3.html"><span class="bold">third item</span></a></li>
         <li class="item-1 active"><a href="link4.html">fourth item</a></li>
         <li class="item-0"><a href="link5.html">fifth item</a></li>
     </ul></div>'''
>>> pq(html)('li') # 获取所以li元素 list
[<li.item-0>, <li.item-1>, <li.item-0.active>, <li.item-1.active>, <li.item-0>]
>>> pq(html)('li').items()  # 获取所以li元素 生成器
>>> pq(html)('li').outerHtml()  # 获取第一个元素的html表示形式
'<li class="item-0">first item</li>'

# 获取id等于haha下面的class等于item-0下的a标签下的span标签（注意层级关系以空格隔开）
>>> doc = pq(html)
>>> doc('#haha .item-0 a span') # <span class="bold">third item</span>
>>> d = doc('#haha .item-0.active')
>>> d.siblings() # 兄弟元素
[<li.item-1>, <li.item-0>, <li.item-1.active>, <li.item-0>]

```

#### 子元素父元素
```
item = doc('div ul')
print(item)
#我们可以通过已经查找到的元素，再此查找这个标签下面的元素
print(item.parent())   # 通过.parent就可以找到父元素的内容
print(item.children())  #  获取子元素
item.children('.item-0')  # 通过css选择器过滤子元素
```


#### 获取属性信息、文本
```
>>> item = doc(".item-0.active a")
>>> item.attr.href  # 'link3.html'
>>> item.attr('href')  # 'link3.html'
>>> item.text() # 'third item'
>>> item.html()  # 获取当前元素下的html
'<span class="bold">third item</span>'
```
#### 元素查找
```
>>> m = '<p><span><em>Whoah!</em></span></p><p><em> there</em></p>'
>>> d = pq(m)
>>> d('p').find('em')  # 查找p元素下的所以em元素
[<em>, <em>]
>>> d('p').eq(1).find('em').html()  # 通过索引指定查找范围 eq(1) 第二个p元素下查找
' there'
```

#### 过滤
```
>>> d = pq('<p class="hello">Hi</p><p>Bye</p>')
>>> d('p').filter('.hello').outerHtml()   # 通过css选择器过滤p元素下的class为hello的元素
'<p class="hello">Hi</p>'
>>> d('p').filter(lambda i: i == 1).outerHtml()  # 通过函数
'<p>Bye</p>'
>>> d('p').filter(lambda i, this: pq(this).text() == 'Hi')
[<p.hello>]
```


