

#### 基本操作

进制转换及 整数和ASCII互转

```
>>> bin(10) # 十进制转换为二进制
'0b1010'
>>> oct(8)  # 十进制转换为八进制
'0o10'
>>> hex(15) # 十进制转换为十六进制
'0xf'
>>> chr(65) # 十进制整数对应的ASCII字符
'A'
>>> ord("A") # ASCII字符对应的十进制数
65
```

复数、四舍五入、商和余数

```
>>> complex(1,2) # 创建复数
(1+2j)
>>> round(0.227,2) # 保留2位小数
0.23
>>> divmod(10,3)  # 商和余数
(3, 1)
```

不可变集合

```
>>> a = frozenset([1,1,3,2,3])
>>> a.add(1) # 因为不可修改，所以没有像set那样的add和pop方法
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'frozenset' object has no attribute 'add'
>>> a
frozenset({1, 2, 3})
```

查看变量占字节数

```
>>> a = [('a',1),('b',2)]
>>> sys.getsizeof(a)
80
>>> a = {'a':1,'b':2.0} 
>>> sys.getsizeof(a)
240  # 字典比列表占用更多空间
```

快速复制

```python
>>> a = [1,3,5] * 3  # [1, 3, 5, 1, 3, 5, 1, 3, 5]
>>> a[0] = 10  # [10, 3, 5, 1, 3, 5, 1, 3, 5]
# 如果列表元素为列表或字典等复合类型
a = [[1,3,5],[2,4]] * 3 # [[1, 3, 5], [2, 4], [1, 3, 5], [2, 4], [1, 3, 5], [2, 4]]
a[0][0] = 10 #  
# 结果可能出乎你的意料，其他a[1[0]等也被修改为10
[[10, 3, 5], [2, 4], [10, 3, 5], [2, 4], [10, 3, 5], [2, 4]]
# 这是因为*复制的复合对象都是浅引用，也就是说id(a[0])与id(a[2])门牌号是相等的
```

字符串驻留

```
>>> a = "devopshot"
>>> b = "devops" +"hot"
>>> id(a) == id(b)  # True
>>> a = "@devops.com"
>>> b = "@devops" + ".com"
>>> id(a) == id(b) #False
# 这与Cpython 编译优化相关，行为称为字符串驻留，但驻留的字符串中只包含字母，数字或下划线
```

执行时机

```
>>> array = [1,3,5]
>>> g = (x for x in array if array.count(x) >0)
>>> array = [5,7,9]
>>> list(g) # [5]
# 生成器表达式中, in 子句在声明时执行, 而条件子句则是在运行时执行
# 等价于 g = (x for x in [1,3,5] if [5,7,9].count(x) > 0)
```

条件复制`x=1 if (y==10) else 2`

列表拷贝 

```
 x = [1,2,3]
 y = x[:]
```

列表重构

```
>>> l = [[1,2,3],[4,5],[6],[7,8,9]]
>>> l
[[1, 2, 3], [4, 5], [6], [7, 8, 9]]
>>> sum(l,[])
[1, 2, 3, 4, 5, 6, 7, 8, 9]
```

列表去重

```
# 用集合
list(set(l))
# 用字典
{}.fromkeys(l1).keys()      比set快
```

字典生成

```
{a:a**2 for a in range(1,10)}
```

dict删除key

```
要删除的key数量较多(超多一半)的话，建议重新生成dict；如果数量较少，在pop和del都可以的情况下，del稍快一些

python3 -m timeit -s "d = {'f':1,'foo':2,'bar':3}" "d1 = d.copy()" "for k in d1.keys():" "  if k.startswith('f'):" "    del d[k]"
1000000 loops, best of 3: 0.533 usec per loop

# python3 -m timeit -s "d = {'f':1,'foo':2,'bar':3}" "d1 = d.copy()" "for k in d1.keys():" "  if k.startswith('f'):" "    d.pop(k)"
1000000 loops, best of 3: 0.551 usec per loop
# 速度基本一样
```

找列表中最大、最小值下标

```
max(range(len(a)), key=a.__getitem__)
min(range(len(a)), key=a.__getitem__)
```

判断奇数

```
# 自然是使用位操作最快了
if a & 1:
    print'it is even'
```

while 1 比 while True 更快, 但是后者可读性强

使用级联比较x < y < z 

使用join合并迭代器中的字符串

优化包含多个判断表达式的顺序(惰性计算)

```
# 对于and，应该把满足条件少的放在前面，对于or，把满足条件多的放在前面。如：
# python3 -m timeit -n 100 'a = range(2000)' '[i for i in a if 1000<i<2000 or 10 <i<20]'
100 loops, best of 3: 172 usec per loop 
# python3 -m timeit -n 100 'a = range(2000)' '[i for i in a if 10<i <20 or 1000< i<2000]'
100 loops, best of 3: 227 usec per loop 

# python3 -m timeit -n 100 'a = range(2000)' '[i for i in a if i>1900 and i% 2 == 0]'
100 loops, best of 3: 80 usec per loop 
# python3 -m timeit -n 100 'a = range(2000)' '[i for i in a if i%2 == 0 and i >1900]'
100 loops, best of 3: 175 usec per loop
```

不借助中间变量交换两个变量的值

```
使用a,b=b,a
而不是c=a;a=b;b=c;来交换a,b的值，可以快1倍以上。
```

幂计算使用**而不是pow

```
# python3  -m timeit -n 10000 'c = pow(2,20)'
10000 loops, best of 3: 0.4 usec per loop
# python3 -m timeit -n 10000 '2**20'
10000 loops, best of 3: 0.0205 usec per loop
```

使用if is

```
# python3 -m timeit -n 100 'a = range(10000)' '[i for i in a if i is True]'
100 loops, best of 3: 456 usec per loop
# python3 -m timeit -n 100 'a = range(10000)' '[i for i in a if i == True]'
100 loops, best of 3: 579 usec per loop
```

选择合适的格式化字符方式

```
# python3 -m timeit -n 100000 's1,s2 = "ax","bx"' '"abc"+s1+s2'
100000 loops, best of 3: 0.106 usec per loop
# python3 -m timeit -n 100000 's1,s2 = "ax","bx"' '"abc{0}{1}".format(s1,s2)
'100000 loops, best of 3: 0.306 usec per loop
# python3 -m timeit -n 100000 's1,s2 = "ax","bx"' '"abc%s%s" % (s1,s2)'
100000 loops, best of 3: 0.204 usec per loop
三种情况中，format的方式是最慢的，但是三者的差距并不大（都非常快）。(个人觉得%的可读性最好)
```

合理使用生成器（generator）和yield

```
# python -m timeit -n 100  'a = (i for i in range(100000))'
100 loops, best of 3: 1.27 msec per loop
# python -m timeit -n 100  'a = [i for i in range(100000)]'
100 loops, best of 3: 5.16 msec per loop
使用()得到的是一个generator对象，所需要的内存空间与列表的大小无关，所以效率会高一些。在具体应用上，比如set(i for i in range(100000))会比set([i for i in range(100000)])快。
但是对于需要循环遍历的情况

# python -m timeit -n 10  'for x in (i for i in range(100000)): x'
10 loops, best of 3: 10.8 msec per loop
# python3 -m timeit -n 10  'for x in [i for i in range(100000)]: x'
10 loops, best of 3: 9.38 msec per loop
# 后者的效率反而更高，但是如果循环里有break,用generator的好处是显而易见的
```

使用dict或set查找元素

```
# python3 -m timeit -n 10000  'a = range(1000)' 's = set(a)' '100 in s'
10000 loops, best of 3: 26.7 usec per loop 
# python3 -m timeit -n 10000  'a = range(1000)' 'd = {}.fromkeys(a)' '100 in d'
10000 loops, best of 3: 32.7 usec per loop 
# python3 -m timeit -n 10000  'a = range(1000)' 'd = dict((i,1) for i in a)' '100 in d'
10000 loops, best of 3: 92.4 usec per loop 
```

合理使用copy与deepcopy

```
这两个函数的不同之处在于后者是递归复制的。效率也不一样
# python -m timeit -n 10 'import copy'  'a = range(100000)' 'copy.copy(a)'
10 loops, best of 3: 2.1 msec per loop
# python -m timeit -n 10 'import copy'  'a = range(100000)' 'copy.deepcopy(a)'
10 loops, best of 3: 132 msec per loop
```

#### 函数和模块

1. 操作函数对象

   ```
   >>> def f(): print("i'm f")
   >>> def g(): print("i'm g")
   >>> [f,g][1]() #i'm g
   >>> [f,g][0]() # i'm f
   # 创建函数对象的list，根据想要调用的index，方便统一调用
   ```

2. 逆序序列

   ```
   >>> list(range(10,-1, -1)) # [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
   # 第三个参数为负时，表示从第一个参数开始递减，终止到第二个参数(不包括此边界)
   ```

3. 函数参数

   ```
   # 位置参数，关键字参数，默认参数，可变位置或关键字参数
   >>> def f(a, *b, c=10, **d): # 默认参数c不能位于可变关键字参数d后
   ...  print(f'a:{a}, b:{b}, c:{c}, d:{d}')
   >>> f(1,2,5,w=10,h=20)
   a:1, b:(2, 5), c:10, d:{'w': 10, 'h': 20}
   # 可变位置参数b实参后被解析为元组(2,5);而c取得默认值10; d被解析为字典.
   >>> f(a=1, c=12)
   a:1, b:(), c:12, d:{}
   # a=1传入时a就是关键字参数，b,d都未传值，c被传入12，而非默认值
   # 注意观察参数a, 既可以f(1),也可以f(a=1) 其可读性比第一种更好，建议使用f(a=1)。如果要强制使用f(a=1)，需要在前面添加一个星号
   def f2(*,a,**b): # 前面的*发挥作用是只能传入关键字参数 非关键字参数将报错
     print(f'a:{a},b:{b}')
   # 查看参数类型
   >>> for name,val in inspect.signature(f).parameters.items():
   ...  print(name, val.kind) 
   a POSITIONAL_OR_KEYWORD
   b VAR_POSITIONAL
   c KEYWORD_ONLY
   d VAR_KEYWORD
   
   >>> for name,val in inspect.signature(f2).parameters.items():
   ...  print(name, val.kind)
   a KEYWORD_ONLY
   b VAR_KEYWORD
   ```

4. groupby分组

   ```
   # 分组前必须按照分组字段排序
   a = ['aa', 'ab', 'abc', 'bcd', 'abcde', 'aa']
   >>> [(name, list(group)) for name, group in groupby(a,len)]  # 未排序
   [(2, ['aa', 'ab']), (3, ['abc', 'bcd']), (5, ['abcde']), (2, ['aa'])]
   >>> a.sort(key=len)
   ['aa', 'ab', 'aa', 'abc', 'bcd', 'abcde']
   >>> [(name, list(group)) for name, group in groupby(a,len)]
   [(2, ['aa', 'ab', 'aa']), (3, ['abc', 'bcd']), (5, ['abcde'])]
   ```

5. 错误的默认值会导致下面的结果

   ```
   def foo(x=[]):
       x.append(1)
       print(x)
   
   foo()  # [1]
   foo()  # [1, 1]
   # 正确的默认值
   def foo(x=None):
       if x is None:
           x = []
       x.append(1)
       print(x)
   foo() # [1]
   foo() # [1]
   ```

6. 使用 `cProfile,cStringIO和cPickle`等用c实现相同功能（分别对应`profile,StringIO,pickle`）的包

   由c实现的包，速度快10倍以上！（python3中将cpickle 和pickle 合并成pickle）

7. 使用最佳的反序列化方式

   ```
   # 下面比较了eval, cPickle, json方式三种对相应字符串反序列化的效率：
   # python3 -m timeit -n 100  "a = range(10000)" "s1 = str([x for x in a ])" "x = eval(s1)"
   100 loops, best of 3: 15 msec per loop
   # python3 -m timeit -n 100  "import pickle" "a = range(10000)" "s2 = pickle.dumps([x for x in a])" "x = pickle.loads(s2)"
   100 loops, best of 3: 1.15 msec per loop
   # python3 -m timeit -n 100  "import json" "a = range(10000)" "s2 = json.dumps([x for x in a])" "x = json.loads(s2)"
   100 loops, best of 3: 2.66 msec per loop
   ```

8. 函数传参（可变对象传引用，不可变对象传值） 传的是对象或者对象的引用

#### 面向对象

子类继承父类的静态方法？ 子类的实例继承了父类的static_method静态方法，调用该方法，还是调用的父类的方法和类属性。

**可调用接口 __call_**

对象通过提供`__call__(self, *args[, **kwargs]) `方法可以模拟函数行为，如果一个对象x提供了改方法，就可以像函数一样调用它，也就是说，`x(args1,args2,...)`等同于调用`x.__call__(self, args1,args2,...).`

```
class A(object):
    def __init__(self,o):
        self.o = o
    def __call__(self,x):
        return abs(x-self.o)

nums = [1,37,42,101,13,9,-20]
nums.sort(key=A(10))
print(nums) #  [9, 13, 1, 37, -20, 42, 101]
```

定义新异常

所有内置异常都使用类进行定义，要创建新异常，就定义父类为Exception的新类

```
class NetworkError(Exception): pass
# 通过如下方式使用这个新异常
raise NetworkError("Cannot find host.")
```

引发异常时，提供给raise语句的可选值将被用作异常的类构造函数的参数。通常，它就是一个表示某些错误消息的字符串。但是自定义的异常可以带有一个或者多个异常值

```
class DeviceError(Exception):
    def __init__(self, errno, msg):
        self.args = (errno, msg)
        self.errno = errno
        self.msg = msg
raise DeviceError(1, 'Not Responding')
```

类中方法重置

```
class foo:
    def normal_call(self):
        print ("normal_call")
    def call(self):
        print ("first_call")
        self.call = self.normal_call

y = foo()
y.call() # first_call
y.call() # normal_call
y.call() # normal_call
```

动态创建新类`type （类名，父类的元组（针对继承的情况， 可以为空），包含属性的字典（名称和值）｝`

```
NewType = type("NewType",(),{"x":"hello"})
n = NewType()
print(n.x)  # hello
# 等价于
class NewType():
	x = "hello"
```

字典的__missing__内置方法，改方法消消除了KeyError异常，重新定义了找不到Key时的返回

```
class MyDict(dict):
    def __missing__(self,key):
        return key

m = MyDict(a=1,b=2,c=3)
print(m['a'])  # 1
print(m['z'])  # z
```

多继承 旧类和新式类之间采取的（MRO 方法解析顺序） 有所不通

古典类搜索采用的简单的自左至右的深度优先方法 新式类具体采用C3 MRO 方法 具体可以查看类的__mro__ 属性



#### 使用性能分析工具

使用到的timeit模块比较程序执行时间，还有cProfile。cProfile的使用方式也非常简单： python -m cProfile [filename.py](http://filename.py)，[filename.py](http://filename.py) 是要运行程序的文件名，可以在标准输出中看到每一个函数被调用的次数和运行的时间，从而找到程序的性能瓶颈，然后可以有针对性地优化