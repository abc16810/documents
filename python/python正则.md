

#### 常用匹配模式

| 通用正则字符                        |                                                            |
| ----------------------------------- | ---------------------------------------------------------- |
| .                                   | 匹配除换行符`\n`外的所有字符                               |
| ^                                   | 匹配输入字符串的开始位置                                   |
| $                                   | 匹配输入字符串的结束位置                                   |
| \d                                  | 匹配数字 等价于[0-9]                                       |
| \D                                  | 匹配非数字                                                 |
| \w                                  | 匹配字母和数字下划线 等价于[a-zA-Z0-9]                     |
| \W                                  | 匹配非英文字母和数字 等价于[^a-zA-Z0-9]                    |
| \s                                  | 匹配空白字符，如\n \t \b等                                 |
| \S                                  | 匹配 \s 以外的其他任意字符                                 |
| \A                                  | 匹配字符串开头 它和’^’的区别是，’/A’只匹配整个字符串的开头 |
| \Z                                  | 匹配字符串结尾 它和’$’的区别是，’/Z’只匹配整个字符串的结尾 |
| \b                                  | 匹配单词边界                                               |
| *                                   | 前面的原子重复0次、1次、多次                               |
| ?                                   | 前面的原子重复0次或者1次                                   |
| +                                   | 前面的原子重复1次或多次                                    |
| {n}                                 | 前面的原子出现了 n 次                                      |
| {n,}                                | 前面的原子至少出现 n 次                                    |
| {n,m}                               | 前面的原子出现次数介于 n-m 之间                            |
| (?(id/name)yes-pattern\|no-pattern) | 判断指定组是否已匹配，执行相应的规则                       |

#### 基本函数

**findall(pattern, string, flags=0)**返回结果结果是一个列表，中间存放的是符合规则的字符串。如果没有符合规则的字符串被找到，就返回一个空列表

**match(pattern, string, flags=0)** 只有当被搜索字符串的开头匹配模式的时候它才能查找到匹配对象  。

**search(pattern, string, flags=0)**  匹配任意位置的首次匹配  即查找到一个匹配项之后停止继续查找

这两个函数唯一的区别是：match从字符串的开头开始匹配，如果开头位置没有匹配成功，就算失败了；而search会跳过开头，继续向后寻找是否有匹配的字符串。

如果匹配不成功，它们则返回一个NoneType

**compile(pattern, flags=0)**直接使用`findall ()`的方式来匹配字符串，一次两次没什么，如果是多次使用的话，由于正则引擎每次都要把规则解释一遍，而规则的解释又是相当费时间的，所以这样的效率就很低 了。如果要多次使用同一规则来进行匹配的话，可以使用`re.compile`函数来将规则预编译

**flags**

- I     IGNORECASE忽略大小写区别
- L    LOCALE字符集本地化
- M   MULTILINE多行匹配。
- S    DOTALL `.`号将匹配所有的字符。缺省情况下’.’匹配除换行符`\n`外的所有字符，使用这一选项以后，`.`就能匹配包括`\n`的任何字符了

**finditer(pattern, string, flags=0)** finditer函数和findall函数的区别是，findall返回所有匹配的字符串，并存为一个列表，而finditer则并不直接返回这些字符串，而是返回一个迭代器。

**sub(pattern, repl, string, count=0, flags=0)**

**subn(pattern, repl, string, count=0, flags=0 )**

这两个函数的唯一区别是返回值。sub返回一个被替换的字符串,subn返回一个元组，第一个元素是被替换的字符串，第二个元素是一个数字，表明产生了多少次替换。



#### **编译后的Pattern对象**

将一个正则式，使用compile函数编译，不仅是为了提高匹配的速度，同时还能使用一些附加的功能。编译后的结果 生成一个Pattern对象，这个对象里面有很多函数，他们看起来和re模块的函数非常象，它同样有findall , match , search ,finditer , sub , subn , split 这些函数，只不过它们的参数有些小小的不同。一般说来，re模块函数的第一个参数，即正则规则不再需要了，应为规则就包含在Pattern对象中了，编译 选项也不再需要了，因为已经被编译过了。因此re模块中函数的这两个参数的位置，就被后面的参数取代了。

findall , match , search 和finditer这几个函数的参数是一样的，除了少了规则和选项两个参数外，它们又加入了另外两个参数，它们是：查找开始位置和查找结束位置，也就是 说，现在你可以指定查找的区间，除去你不感兴趣的区间。它们现在的参数形式是

**findall ( string[, pos[,endpos] ] )**

**finditer ( string [, pos[,endpos] ] )**

**match ( string[, pos[,endpos] ] )**

**search ( string[, pos [,endpos] ] )**

```
>>> p = re.compile(r'(?P<name>[a-z]+)\s+(?P<age>\d+)\s+(?P<tel>\d+).*',re.I)
>>> p.groupindex # 规则里的组
mappingproxy({'name': 1, 'age': 2, 'tel': 3})
# 正则式中的每个组都有一个序号，它是按定义时从左到右的顺序从1开始编号的。其实，re的正则式还有一个0号组，它就是整个正则式本身
>>> p.pattern  # 查询编译时的规则
'(?P<name>[a-z]+)\\s+(?P<age>\\d+)\\s+(?P<tel>\\d+).*'
>>> m = p.search("Tom 24 6446687 ==")
>>> m.groups() ## 看看匹配的各组的情况
('Tom', '24', '6446687')
>>> m.group('name') # 'Tom'
>>> m.group(1) # 'Tom'
>>> m.group(0) # 'Tom 24 6446687 =='
#  原来0组就是整个正则式,包括没有被包围到组里面的内容。当获取0组的时候，你可以不写这个参数。m.group(0)和m.group()的效果是一样的
```

**group([index|id])**  获取匹配的组，缺省返回组0,也就是全部值

**groups()**                   返回全部的组

**groupdict()**             返回以组名为key，匹配的内容为values的字典

**expand( template )** 根据一个模版用找到的内容替换模版里的相应位置,它使用\g<index|name>或 \index 来指示一个组

```
>>> m.expand(r'name is \g<1>, age is \g<age>,tel is \g<3>')
'name is Tom, age is 24,tel is 6446687'
```

正则中字符 `r`。经常见过正则表达式前有一个字符 `r`，它的作用是告诉解释器后面的一串是原生字符串 如`s1 = r'\n.*'` 它告诉编译器s1字符串第一个字符是`\`，第二个字符是`n`



#### 贪婪非贪婪

量词(比如 * 和 +)匹配尽可能多的字符, 称为贪婪模式，当加一个问号在后面时（.*?）它将变为“非贪婪”

```
html='Hello <a href="http://devopshot.com" title="devopshot">devopshot</a>'\
       'Hello <a href="http://example.com" title"example">Example</a>'
>>> re.findall('<a.*>.*<\/a>',html)
['<a href="http://devopshot.com" title="devopshot">devopshot</a>Hello <a href="http://example.com" title"example">Example</a>']
# 贪婪模式尽可能多的匹配，匹配所有<a></a>成一个整体，而不是两个单独<a></a>的匹配
>>> re.findall('<a.*?>.*?<\/a>',html)
['<a href="http://devopshot.com" title="devopshot">devopshot</a>', '<a href="http://example.com" title"example">Example</a>']

```

#### **前向界定符和后向界定符**

`(?=pattern)`一个前向界定符搜索当前的匹配之后搜索匹配，如首先匹配 foo，然后检测是否接着匹配 bar

```
>>> s = "hello foo, hello foobar"
>>> re.search(r'foo(?=bar)', s)  # 匹配foobar的foo
<_sre.SRE_Match object; span=(17, 20), match='foo'>
```

这看起来似乎没什么用，因为我们可以直接检测 foobar 不是更简单么。然而，它也可以用来前向否定界定。 下面的例子匹配foo，当且仅当它的后面没有跟着 bar

```
>>> strs = ["hello foo", "hello foobar", "hello foobaa"]
>>> for s in strs:
...  p = re.search(r'foo(?!bar)', s)
...  if p:
...   print("ok")
...  else:
...   print("no") 
ok
no
ok
```

后向界定符类似，但是它查看当前匹配的前面的模式。你可以使用 (?<=p) 来表示肯定界定，(?<!P) 表示否定界定。如`(?<!foo)bar`   匹配bar前面没有foo的字符

#### **条件(IF-Then-Else)模式**

如匹配尖括号`r'^(<)?[a-z]+(?(1)>)$'`   1 表示分组 (<)，当然也可以为空因为后面跟着一个问号。当且仅当条件成立时它才匹配关闭的尖括号

#### 无捕获组

分组，由圆括号括起来，将会捕获到一个数组，然后在后面要用的时候可以被引用。无捕获组是匹配pattern但不获取匹配的子字符串。也就是说这是一个非获取匹配，不存储匹配的子字符串用于向后引用

```
>>> a = "Hello foobar"
>>> re.search(r'(f.*)(b.*)', a).groups()
('foo', 'bar')
>>> re.search(r'(H.*)(f.*)(b.*)', a).groups()
('Hello ', 'foo', 'bar')
>>> re.search(r'(?:H.*)(f.*)(b.*)', a).groups()
('foo', 'bar')
```

通过在分组的前面添加 **?:**，我们就再也不用在模式数组中捕获它了

#### 命名组

`(?P<pattern>)` 

```
 p = re.compile(r'(?P<name>[a-z]+)\s+(?P<age>\d+)\s+(?P<tel>\d+).*',re.I)
```

#### 常用匹配

- 邮箱 `[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)`

- 国内手机号码`1(3|4|5|6|7|8|9)\d{9}`

- 国内固定电话`\d{3}-\d{8}|\d{4}-\d{7}`   如0511-1234567、021-87654321

- 日期`\d{4}(?:-|\/|.)\d{1,2}(?:-|\/|.)\d{1,2}`

- 中文 `[\u4e00-\u9fa5]`

- 身份证号`[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]`

  ```
  地区：[1-9]\d{5}
  年的前两位：(18|19|([23]\d))       1800-2399
  年的后两位：\d{2}
  月份：((0[1-9])|(10|11|12))
  天数：(([0-2][1-9])|10|20|30|31)          闰年不能禁止29+
  三位顺序码：\d{3}
  校验码：[0-9Xx]
  ```