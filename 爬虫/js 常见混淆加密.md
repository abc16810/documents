Javascript 作为一种运行在客户端的脚本语言，其源代码对用户来说是完全可见的。但不是每个网站的js都能被直接阅读，比如网站反爬或者恶意软件。为了增加代码阅读分析难度，通过混淆（obfuscate）工具对JS代码混淆

常见混淆手段

#### eval加密

这类混淆的关键思想在于将需要执行的代码进行一次编码，在执行的时候还原出浏览器可执行的合法的脚本，然后执行之。看上去和可执行文件的加壳有那么点类似。Javascript 提供了将字符串当做代码执行（evaluate）的能力，可以通过 [Function 构造器](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Function)、[eval](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/eval)、[setTimeout](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/setTimeout)、[setInterval ](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/setInterval)将字符串传递给 js 引擎进行解析执行。其最明显的特征是生成的代码以 `eval(function(p,a,c,k,e,r))` 开头

![1647567705732](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647567705732.png)

无论代码如何进行变形，其最终都要调用一次 eval 等函数。解密的方法不需要对其算法做任何分析，只需要简单地找到这个最终的调用，改为 `console.log` 或者其他方式，将程序解码后的结果按照字符串输出即可。通过在线js解密 [go](https://www.sojson.com)

#### 复杂化表达式

代码混淆不一定会调用 eval，也可以通过在代码中填充无效的指令来增加代码复杂度，极大地降低可读性。Javascript 中存在许多称得上丧心病狂的特性，这些特性组合起来，可以把原本简单的字面量（Literal）、成员访问（MemberExpression）、函数调用（CallExpression）等代码片段变得难以阅读。

Js 中的字面量有字符串、数字、正则表达式

下面简单举一个例子：

1. 访问一个对象的成员有两种方法——点运算符和下标运算符。调用 window 的 eval 方法，既可以写成 `window.eval()`，也可以 `window['eval']`；
2. 为了让代码更变态一些，混淆器选用第二种写法，然后再在字符串字面量上做文章。先把字符串拆成几个部分：`'e' + 'v' + 'al'`；
3. 这样看上去还是很明显，再利用一个数字进制转换的技巧：`14..toString(15) + 31..toString(32) + 0xf1.toString(22)`；
4. 把数字也展开：`(0b1110).toString(4<<2) + (' '.charCodeAt() - 1).toString(Math.log(0x100000000) / Math.log(2)) + 0xf1.toString(11 << 1)`；
5. 最后的效果：`window[(2*7).toString(4<<2) + (' '.charCodeAt() - 1).toString(Math.log(0x100000000) / Math.log(2)) + 0xf1.toString(11 << 1)]('alert(1)')`

在 js 中可以找到许多这样互逆的运算，通过使用随机生成的方式将其组合使用，可以把简单的表达式无限复杂化

#### 复杂的代码混淆

最近在分析数据的时候遇到了网站js类似如下代码混淆

![1647568916954](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647568916954.png)

观察其代码风格，发现这个混淆器做了这几件事：

- 字符串字面量混淆：首先提取全部的字符串，在全局作用域创建一个字符串数组，同时转义字符增大阅读难度，然后将字符串出现的地方替换成为数组元素的引用

- 变量名混淆：不同于压缩器的缩短命名，此处使用了下划线加数字的格式，变量之间区分度很低，相比单个字母更难以阅读

- 成员运算符混淆：将点运算符替换为字符串下标形式，然后对字符串进行混淆

- 删除多余的空白字符：减小文件体积，这是所有压缩器都会做的事

经过搜索，这样的代码很有可能是通过 [javascriptobfuscator.com](http://javascriptobfuscator.com/Javascript-Obfuscator.aspx) 的免费版生成的。其中免费版可以使用的三个选项（Encode Strings / Strings / Replace Names）也印证了前面观察到的现象

这些变换中，变量名混淆是不可逆的。要是可以智能给变量命名的工具也不错，比如这个 [jsnice](http://jsnice.org/) 网站提供了一个在线工具，可以分析变量具体作用自动重命名。



相关参考推荐

https://blog.knownsec.com/2015/08/use-estools-aid-deobfuscate-javascript/

[反爬虫JS破解与混淆还原手册](https://github.com/LoseNine/Restore-JS)

