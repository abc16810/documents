beautifulsoup4基本使用


简介
Beautiful Soup 是一个可以从HTML或XML文件中提取数据的Python库.它能够通过你喜欢的转换器实现惯用的文档导航,查找,修改文档的方式.在爬虫方面常用于对html文档解析，目前最新版本4.4.0

安装
```
pip install beautifulsoup4
```

解析器

> `lxml HTML` 解析器  BeautifulSoup(markup, "lxml")  官方推荐使用。
在Python2.7.3之前的版本和Python3中3.2.2之前的版本,必须安装lxml或html5lib, 因为那些Python版本的标准库中内置的HTML解析方法不够稳定.


#### ﻿基本使用

BeautifulSoup 的构造方法,就能得到一个文档的对象, 可以传入一段字符串或一个文件句柄.

```
from bs4 import BeautifulSoup

soup = BeautifulSoup(open("index.html"))
soup = BeautifulSoup("<html>data</html>")

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>
<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
<p class="story">...</p>
"""

soup = BeautifulSoup(html,'lxml')   # 建议手动指定解析器 以便Beautiful Soup跨平台不同的虚拟环境提供相同的解析结果
print(soup.prettify())  # 美化输出
print(soup.title)  # <title>The Dormouse's story</title> 获取title标签内容
print(soup.title.name)  # 获得该title标签的名称，即'title'
print(soup.title.string)  # 获取title标签里的内容 即文本信息 'the Dormouse's story'
print(soup.title.parent.name) # #获取父标签的名字 即 'name'
print(soup.p)  # 获取第一个p标签
print(soup.p["class"])  # 获取第一个p标签的'class'的属性值 即 title
print(soup.a)   # 获取第一个a标签
print(soup.find_all('a'))  # 获取元素下的所有a标签
print(soup.find(id='link3')) # 查找id=link3的标签

```

#### 对象的种类

Beautiful Soup将复杂HTML文档转换成一个复杂的树形结构,每个节点都是Python对象,所有对象可以归纳为4种: `Tag `, `NavigableString` , `BeautifulSoup` , `Comment`

##### TAG 对象方法和属性

 - Name  名称
 - Attributes 属性
 - 多值属性
 - 可以遍历的字符串 string
 - contents  以列表的形式输出 （直接子节点）
 - children  返回生成器  （直接子节点）
 - descendants   递归子孙节点
 - string  (tag仅有一个子节点)
 - strings  遍历所有字符串
 - parent/parents  父节点

```
>>> type(soup.title)
<class 'bs4.element.Tag'>

# 每个tag都有自己的名字,通过 .name 来获取
>>> soup.title.name
# 一个tag可能有很多个属性，通过属性名称或者.attrs , 在Beautiful Soup中多值属性的返回类型是list
# soup.p['class']   或者 soup.p.attrs   
>>> css_soup = BeautifulSoup('<p class="body strikeout"></p>')
>>> css_soup.p['class']
['body', 'strikeout']

# 如果转换的文档是XML格式,那么tag中不包含多值属性

>>> xml_soup = BeautifulSoup('<p class="body strikeout"></p>', 'xml')
>>> xml_soup.p['class'] # u'body strikeout'

# 可以遍历的字符串 字符串常被包含在tag内.Beautiful Soup用 NavigableString 类来包装tag中的字符串
# tag中包含的字符串不能编辑,但是可以被替换成其它的字符串,用 replace_with() 方法:
>>> soup.p
<p class="title"><b>The Dormouse's story</b></p>
>>> soup.p.string # "The Dormouse's story"
>>> soup.p.string.replace_with("aaa")
>>> soup.p.string # 'aaa'

# tag的 .contents 属性可以将tag的子节点以列表的方式输出
>>> soup.title.contents
["The Dormouse's story"]

# 字符串没有 .contents 属性,因为字符串没有子节点:
>>> soup.title.contents[0].contents # AttributeError

# 注释
markup = "<b><!--Hey, buddy. Want to buy a used parser?--></b>"
soup = BeautifulSoup(markup)
comment = soup.b.string
type(comment) # <class 'bs4.element.Comment'>

# 通过tag的 .children 生成器,可以对tag的子节点进行循环:
>>> for c in soup.head.children:
...  print(c) # <title>The Dormouse's story</title>

# .descendants 递归子孙节点
>>> for x in soup.head.descendants:
...  print(x)
... 
<title>The Dormouse's story</title>
The Dormouse's story

# 如果tag只有一个 NavigableString 类型子节点,那么这个tag可以使用 .string 得到子节点
>>> soup.head.string  # "The Dormouse's story"
# 如果tag包含了多个子节点,tag就无法确定 .string 方法应该调用哪个子节点的内容, .string 的输出结果是 None
print(soup.html.string) # None

# .strings 和 stripped_strings   如果tag中包含多个字符串,可以使用 .strings 来循环获取，输出的字符串中可能包含了很多空格或空行,使用 .stripped_strings 可以去除多余空白内容
list(soup.stripped_strings)

# parent  父节点   文档的顶层节点比如<html>的父节点是 BeautifulSoup 对象:  BeautifulSoup 对象的 .parent 是None:

# 同一个元素的子节点,可以被称为兄弟节点
# 使用 .next_sibling 和 .previous_sibling 属性来查询兄弟节点
>>> sibling_soup = BeautifulSoup("<a><b>text1</b><c>text2</c></b></a>")
>>> sibling_soup.b # <b>text1</b>
>>> sibling_soup.b.next_sibling  # <c>text2</c>

```

#### 遍历文档树

`find(name,attrs,recursive,text,**kwargs)`，`find_all(name,attrs,recursive,text,**kwargs)`
搜索当前tag的所有tag子节点,并判断是否符合过滤器的条件，唯一的区别是 find_all() 方法的返回结果是值包含一个元素的列表,而 find() 方法直接返回结果.

```
soup.find_all('a')  # 查找文档中所有的<a>标签:
soup.find_all('p',attrs={'class': 'story'})
soup.find_all('p',{'class': 'story'})   soup.find_all(class_='story')
soup.find_all('p', 'title')     返回的是CSS Class为”title”的<p>标签
soup.find(text=re.compile("sisters"))   # 通过正则表达式的 match() 来匹配内容， 批评文本中包括`sisters`文本
soup.find_all(id="link2")   #kwargs  指定关键字  搜索每个tag的`id`属性
soup.find_all(href=re.compile("elsie"))   # 搜索每个tag的”href”属性
soup.find_all(id=True) # 查找所有包含 id属性的tag,无论 id 的值是什么
soup.find_all(href=re.compile("elsie"), id='link1') # 使用多个指定名字的参数可以同时过滤tag的多个属性
soup.find_all(re.compile('^p'))   # 找出所有以p开头的标签
soup.find_all(["a", "b"])  # 列表参数,Beautiful Soup会将与列表中任一元素匹配的内容返回
soup.find_all(True)  #  True 可以匹配任何值,下面代码查找到所有的tag,但是不会返回字符串节点
# 有些tag属性在搜索不能使用,比如HTML5中的 data-* 属性:
data_soup = BeautifulSoup('<div data-foo="value">foo!</div>')
data_soup.find_all(data-foo="value")
# SyntaxError: keyword can't be an expression
# 但是可以通过 find_all() 方法的 attrs 参数定义一个字典参数来搜索包含特殊属性的tag
data_soup.find_all(attrs={"data-foo": "value"})

```

**方法**

如果没有合适过滤器,那么还可以定义一个方法,方法只接受一个元素参数,如果这个方法返回 True 表示当前元素匹配并且被找到,如果不是则反回 False

```
def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')
soup.find_all(has_class_but_no_id)

# 找出 href 属性不符合指定正则的 a 标签
def not_lacie(href):
    return href and not re.compile("lacie").search(href)
soup.find_all(href=not_lacie)
```

**CSS搜索**

按照CSS类名搜索tag的功能非常实用,但标识CSS类名的关键字 class 在Python中是保留字,使用 class 做参数会导致语法错误.从Beautiful Soup的4.1.1版本开始,可以通过 class_ 参数搜索有指定CSS类名的tag

class_ 参数同样接受不同类型的过滤器,字符串,正则表达式,方法或 True

tag的 class 属性是多值属性,按照CSS类名搜索tag时,可以分别搜索tag中的每个CSS类名:

```
soup.find_all("a", class_="sister")
soup.find_all(class_=re.compile('itl'))
def has_six_characters(css_class):
    return css_class is not None and len(css_class) == 6

soup.find_all(class_=has_six_characters)

```

通过 string 参数可以搜搜文档中的字符串内容.与 name 参数的可选值一样, string 参数接受 字符串, 正则表达式 , 列表, True  (之前为text参数)

```
soup.find_all(string="Elsie")
# [u'Elsie']
soup.find_all(string=["Tillie", "Elsie", "Lacie"])
# [u'Elsie', u'Lacie', u'Tillie']
soup.find_all(string=re.compile("Dormouse"))
soup.find_all("a", string="Elsie") # 搜索内容里面包含“Elsie”的<a>标签
def is_the_only_string_within_a_tag(s):
    """Return True if this string is the only child of its parent tag."""
    return (s == s.parent.string)

soup.find_all(string=is_the_only_string_within_a_tag)
```

find_all() 方法返回全部的搜索结构,如果文档树很大那么搜索会很慢.如果我们不需要全部结果,可以使用limit参数限制返回结果的数量.
效果与SQL中的limit关键字类似,当搜索到的结果数量达到 limit 的限制时,就停止搜索返回结果
```
soup.find_all("a", limit=2)  # 限制了返回数量
```

`recursive` 参数调用tag的 find_all() 方法时,Beautiful Soup会检索当前tag的所有子孙节点,如果只想搜索tag的直接子节点,可以使用参数 `recursive=False`
```
soup.html.find_all("title", recursive=False)
```


#### CSS选择器
在 Tag 或 BeautifulSoup 对象的.select() 方法中传入字符串参数, 即可使用CSS选择器的语法找到tag


```
soup.select("title")
soup.select("body a")   # 查询所有的a标签   逐层查找:

# 找到某个tag标签下的直接子标签
soup.select("p > a")
soup.select("head > title")
soup.select("p > a:nth-child(2)")  或者soup.select("p > a:nth-of-type(2)")
soup.select("p > #link2")

# 找到兄弟节点标签
soup.select("#link1 + .sister")     # 选择紧接在另一个元素后的元素，而且二者有相同的父元素。只会选择第一个相邻的匹配元素
soup.select("#link1 ~ .sister")     # 匹配所有在#link1元素之后的同级类名为sister的元素。


# 通过CSS的类名查找
soup.select('.sister')  或者soup.select("[class=sister]")、soup.select("[class~=sister]")


# 通过tag的id查找
soup.select('#link3')
soup.select('a#link3')

# 通过是否存在某个属性来查找
soup.select('a[href]')

# 通过属性的值来查找
soup.select('a[href="http://example.com/elsie"]')   精确查找
soup.select('a[href^="http://example.com/"]')    以http://example.com/开头查找
soup.select('a[href$="tillie"]')  以tillie结尾查找
soup.select('a[href*=".com/el"]')   包含查找
```


