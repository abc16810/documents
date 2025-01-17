#### xpath
基本用法

 - nodename	选取此节点的所有子节点。
 - /		从根节点选取。
 - //		从匹配选择的当前节点选择文档中的节点，而不考虑它们的位置。
 - .		选取当前节点。
 - ..		P选取当前节点的父节点。
 - @		选取属性。
 - \*	匹配任何元素节点。  如   "//* 选取文档中的所有元素。"     
 - @*	匹配任何属性节点。	"//a[@*]  选取所有带有属性的 a元素"


```


html = """<html><head>
	  <base href="http://example.com/">
	  <title>Example website</title>
	 </head>
	 <body>
	  <div id="images">
	   <a href="image1.html">Name: My image 1 <br><img src="image1_thumb.jpg"></a>
	   <a href="image2.html">Name: My image 2 <br><img src="image2_thumb.jpg"></a>
	   <a href="image3.html">Name: My image 3 <br><img src="image3_thumb.jpg"></a>
	   <a href="image4.html">Name: My image 4 <br><img src="image4_thumb.jpg"></a>
	   <a href="image5.html">Name: My image 5 <br><img src="image5_thumb.jpg"></a>
	   <p class='ppp cc'> this is a test </p>
	   <p> this is a test2 </p>
	  </div>
	</body></html>"""
	
>>> from lxml import etree
>>>	html = etree.HTML(html)

>>>	html.xpath('body') 表示选取 body 元素的所有子节点
>>>	html.xpath('/html') 表示选取根元素 html
>>>	html.xpath('body/div/a') 选取属于 body下的div下的子元素的所有 a 元素。
>>>	html.xpath('//a') 选取所有 a 元素，而不管它们在文档中的位置。
>>>	html.xpath('body//a') 选择属于 body 元素的后代的所有 a 元素，而不管它们位于 body 之下的什么位置。
>>>	html.xpath('//@href') 选取名为 href 的所有属性。

>>> html.xpath("//title/text()")  # 打印title文本信息   列表的形式
['Example website']

>>> html.xpath("//html/body/div/a[1]")  # 打印第一个a元素
>>> html.xpath('/html/body/div/a[last()]')   # 最后一个
>>> html.xpath('/html/body/div/a[last()-1]')   # 倒数第二个

>>> html.xpath("//a[@href]")  # 获取所有拥有href的a属性
[<Element a at 0x7f1a7ba6b3c0>, <Element a at 0x7f1a7bac9900>, ...]  
>>> html.xpath('//a[@href="image5.html"]')  # 获取href为image5.html的a属性
>>> html.xpath('//div/a | //div/p')   选取 div 元素的所有 a元素 或 p 元素
>>> html.xpath('//p[not(@class)]')  # not排除属性

```

**函数**


```
# starts-with 函数 属性以什么开始
>>> html.xpath('//a[starts-with(@href, "image")]')
# contains 函数包含
>>> html.xpath('//a[contains(@href, "html")]')   # href属性中包含html 的所有a属性
>>> html.xpath('//a[contains(@href, "image1") and contains(@href, "html")]')      # 两个同时匹配
>>> html.xpath('//div/a[contains(text(),"image")]')   # 文本中包含image的a元素
```


#### CSS

```
>>> from pyquery import PyQuery as pq
>>> p = pq(html)

>>> p('*')       # *通配选择器,选择文档中所以HTML元素 
>>> p('a')  	 # E(element)元素选择器,选择指定类型的HTML元素 
>>> p('#images') #ID选择器,选择指定ID属性值为“id”的任意类型元素
>>> p('.ppp')  	 # .class类选择器	,选择指定class属性值为“class”的任意类型的任意多个元素
>>> p('a,p')	 # selector1,selectorN 群组选择器,将每一个选择器匹配的元素集合并 选择所有 <a> 元素和所有 <p> 元素 
>>> p('#images a')
>>> p('#images img') 	 # E F 后代选择器（包含选择器） 选择匹配的F元素，且匹配的F元素被包含在匹配的E元素内
>>> p('#images > a')	 # E>F	子选择器   选择匹配的F元素，且匹配的F元素所匹配的E元素的子元素 	
>>> p('a[href="image2.html"] + a')  #E+F 相邻兄弟选择器  选择匹配的F元素，且匹配的F元素紧位于匹配的E元素的后面 (image3)
>>> p('a[href="image2.html"] ~ a')  #E~F 通用选择器	选择匹配的F元素，且位于匹配的E元素后的所有匹配的F元素	
>>> p('[href]') 	# [attribute] 用于选取带有指定属性的元素,选取带有href属性的 
>>> p('[src="image1_thumb.jpg"]')   # [attribute=value]	用于选取带有指定属性和值的元素。		
>>> p('p[class~="ppp"]') # 	[attribute~=value]	用于选取属性值中包含指定词汇的元素。	
>>> p('[href|="image1.html"]') # 	[attribute|=value]	用于选取带有以指定值开头的属性值的元素，该值必须是整个单词。	
>>> p('[src^="image"]') #	[attribute^=value]	匹配属性值以指定值开头的每个元素。		
>>> p('[src$="jpg"]') # [attribute$=value]	匹配属性值以指定值结尾的每个元素。
>>> p('[src*="b.jpg"]') # [attribute*=value]	匹配属性值中包含指定值的每个元素。		
	
>>> p('div#images > a:first-child')	 #E:fisrt-child	作为父元素的第一个子元素的元素E。与E:nth-child(1)等同			
>>> p('div#images > p:last-child')   #E:last-child	作为父元素的最后一个子元素的元素E。与E:nth-last-child(1)等同	
# E F:nth-child(n)	选择父元素E的第n个子元素F。其中n可以是整数（1，2，3）、关键字（even，odd）、可以是公式（2n+1）,而且n值起始值为1，而不是0.
p('#images p:nth-child(6)')
p('#images p:nth-child(odd)')
p('#images p:nth-child(even)')

p('#images a:nth-child(1)')
p('#images a:nth-child(odd)')  1,3,5   奇数
		
>>> p('a:nth-of-type(5)') #	E:nth-of-type(n)	选择父元素内具有指定类型的第n个E元素			
>>> p('#images p:nth-last-of-type(1)') #	E:nth-last-of-type(n)	选择父元素内具有指定类型的倒数第n个E元素		
	
>>> p('a:first-of-type') #	E:first-of-type	选择父元素内具有指定类型的第一个E元素，与E:nth-of-type(1)等同		
# E:last-of-tye	选择父元素内具有指定类型的最后一个E元素，与E:nth-last-of-type(1)等同
```
