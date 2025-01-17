#### 迭代器

使用`iter(obj, sentinel)` 内置函数, 返回一个可迭代对象, sentinel可省略(一旦迭代到此元素，立即终止)

```
>>> a = [1,2,3]
>>> type(a)
<class 'list'>
>>> ia = iter(a)
>>> type(ia)
<class 'list_iterator'>
>>> dir(ia)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__length_hint__', '__lt__', '__ne__', '__new__', '__next__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__']
>>> ia.__iter__()  # 返回迭代器对象本身
<list_iterator object at 0x7faaf8012b00>
>>> ia.__next__()   # 返回下一个元素，直到异常抛出
1
>>> ia.__next__()
2
>>> ia.__next__()
3
>>> ia.__next__()
StopIteration
```

自己实现迭代器协议创建迭代器对象，实现迭代器协议 就要在类中实现`__iter__()`和`__next__()`方法

```
>>> class ListIter():
...  def __init__(self, data):
...   self.__data = data
...   self.__count = 0
...  def __iter__(self):
...   return self
...  def __next__(self):
...   if self.__count < len(self.__data):
...    val = self.__data[self.__count]
...    self.__count += 1
...    return val
...   else:
...    raise StopIteration
>>> a = ListIter([1,2,3,4,5])
>>> next(a)
1
```

多次迭代

前面的迭代器对象不支持重新迭代，也就是同一个迭代器对象无法多次迭代

```
>>> print ([x for x in a])  
[]
```

解决这个问题就是让迭代器对象本身返回一个迭代器对象

```
class ListIter():
    def __init__(self, data):
        self.__data = data
        self.__count = 0

    def __iter__(self):
        return iter(self.__data)
```



可变对象和迭代器

在 迭代可变对象时候，一个序列的迭代器只是**记录当前到达了序列中的第几个元素 ，所以当过程中改变了序列的元素。更新会立即反应到所迭代的对象上**

```
>>> for x in k:
...  print(x)
...  k.remove(x)
... 
1
3
5
```

迭代器只记录列表中的第几个元素，那么当在第0个元素的时候是1，然后删除1，这是列表为【2，3，4，5】

此时迭代器记录是在第二个位置上面，就指上了新列表中的第二位置上，即3， 让后输出3 

以此类推 只能输出1，3，5

列表最后为【2，4】

\>>> k

[2, 4]

应用，定义一个迭代器，实现对某个正整数的依次递减1，直到0

```
class Desc:
    def __init__(self, n):
        self.n = n
        self.a = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.a < self.n:
            self.n -= 1
            return self.n
        else:
            raise StopIteration

d = Desc(10)
print(list(d))
[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
```

 反向迭代器reversed

```
>>> d = reversed([1,2,3,4])
>>> print(d)
<list_reverseiterator object at 0x7faaf6fcaac8>
>>> print(list(d))
[4, 3, 2, 1]
```

zip 迭代器

```
>>> z = zip([1,2,3],[4,5,6])
```



#### 生成器

**推导式(Comprehensions)**

这是一种将for循环、if表达式以及赋值语句放到单一语句中的一种方法。换句话说，你能够通过一个表达式对一个列表做映射或过滤操作。

```
num = [1,4,-5,10,7,2,4,-1]
filtered_and_squared = [ x**2 for x in num if x > 0]
```

列表推导式被封装在一个列表中，所以很明显它能够立即生成一个新列表。这里只有一个type函数调用而没有隐式调用lambda函数，列表推导式正是使用了一个常规的迭代器、一个表达式和一个if表达式来控制可选的参数。

另一方面，列表推导也可能会有一些负面效应，那就是整个列表必须一次性加载于内存之中，这对上面举的例子而言不是问题，甚至扩大若干倍之后也都不是问题。但是总会达到极限，内存总会被用完。

针对上面的问题，生成器(Generator)能够很好的解决。生成器表达式不会一次将整个列表加载到内存之中，而是生成一个生成器对象(Generator objector)，所以一次只加载一个列表元素。

**生成器表达式同列表推导式有着几乎相同的语法结构，区别在于生成器表达式是被圆括号包围，而不是方括号**

生成器也是迭代器的一种,但是你**只能迭代它们一次**.原因很简单,因为它们不是全部存在内存里,它们只在要调用的时候在内存里生成

```
num=[1,4,-5,10,-7,2,3,-1]
filtered_and_squared=(x**2 for x in num if x > 0)   # 生成器
```

**yield**

Yield是一个与return类似的关键字，通过yield函数将返回一个生成器

```
>>> def create_generator():
...    mylist = range(3)
...    for i in mylist:
...        yield i*i
>>> mygenerator = create_generator() # 创建一个生成器
>>> type(mygenerator)
<class 'generator'>
>>> for i in mygenerator:
...  print(i)
... 
0
1
4
```

当for函数第一次调用从函数中创建的生成器对象时，它将从一开始运行函数中的代码，直到达到yield为止，然后它将返回循环的第一个值。然后，每个后续调用将运行在函数中编写的循环的另一个迭代，并返回下一个值。这将继续，直到生成器被认为是空的。

一旦函数运行并没有碰到yeild语句就认为生成器已经为空了.原因有可能是循环结束或者没有满足if/else之类的

当你的函数要返回一个非常大的集合并且你希望只读一次的话,那么生成器就非常的方便了

```
>>> hasattr(mygenerator, '__iter__')
True
>>> hasattr(mygenerator, '__next__')
True
```

生成器是一个可迭代对象，一个可迭代对象有一个__iter__方法返回一个迭代器。迭代器提供了一个.next (Python 2或.`__next__` (Python 3))方法，该方法会被for循环隐式调用，直到它引发StopIteration。

生成器是创建迭代器的一种方便的方法, 生成器类型是迭代器的子类型

```
>>> import collections, types
>>> issubclass(types.GeneratorType, collections.Iterator)
True
>>> isinstance(mygenerator, collections.Iterator)
True
>>> isinstance(mygenerator, collections.Generator)
True
```

生成器应用

- 遍历目录文件

  ```
  import os
  def tree(top):
      for path, names, fnames in os.walk(top):
          for fname in fnames:
              yield os.path.join(path, fname)
  for name in tree('/tmp/'):
      print (name)
  ```

- List分组

  ```
  from math import ceil
  
  def divide_iter(lst, n):
      if n <= 0:
          yield lst
          return
      i, div = 0, ceil(len(lst) / n)
      while i < n:
          yield lst[i * div: (i + 1) * div]
          i += 1
  >>> list(divide_iter([1,2,3,4,5],2))
  [[1, 2, 3], [4, 5]]
  ```

- 列表全展开

  ```
  #多层列表展开成单层列表
  a=[1,2,[3,4,[5,6],7],8,["python",6],9]
  def function(lst):
      for i in lst:
          if type(i)==list:
              yield from function(i)
          else:
              yield i
  print(list(function(a))) # [1, 2, 3, 4, 5, 6, 7, 8, 'python', 6, 9]
  ```

- 斐波那契数列前n项

  ```
  def fibonacci(n):
      a, b = 1, 1
      for _ in range(n):
          yield a
          a, b = b, a + b
  ```

  

#### 装饰器

装饰器(decorator)是一种高级Python语法。装饰器可以对一个函数、方法或者类进行加工。在Python中，我们有多种方法对函数和类进行加工，比如在Python闭包中，我们见到函数对象作为某一个函数的返回结果。相对于其它方式，装饰器语法简单，代码可读性高。因此，装饰器在Python项目中有广泛的应用。

装饰器可以用def的形式定义，如下面代码中的decorator。装饰器接收一个可调用对象作为输入参数，并返回一个新的可调用对象。装饰器新建了一个可调用对象，也就是下面的new_F。并通过调用F(a, b)来实现原有函数的功能。 定义好装饰器后，我们就可以通过@语法使用 了。

```
def cons_decorator(F):    # 通过cons_decorator装饰器打印输入参数
    def new_F(a,b):
    	print("input",a,b)
        return F(a,b)
    return new_F
    
@cons_decorator
def car(a,b):
    return a
@cons_decorator
def cdr(a,b):
    return b    
```

在函数car和cdr定义之前调用@cons_decorator，我们实际上car和cdr 传递给cons_decorator，并将cons_decorator返回的新的可调用对象赋给原来的函数名(car和cdr)。 所以，当我们调用cdr(3, 4)的时候，就相当于

```
cdr=cons_decorator(cdr)   
cdr(3,4)
```

测试函数运行时间的装饰器

```
import time
from functools import wraps

def timethis(func):
    @wraps(func)  # 正确打印原函数的名称和文档信息
    def wrapper(*args, **kwargs):
        start = time.time()
        print("<function call begin>")
        result = func(*args, **kwargs)
        print("<function call end>")
        end = time.time()
        print(func.__name__, end - start)
        return result
    return wrapper

@timethis
def test_list_append():
    """测试"""
    print(test_list_append.__name__)
    print(test_list_append.__doc__)
    lst=[]
    for i in range(0,100000):
        lst.append(i)

test_list_append()
# 输出
<function call begin>
test_list_append
测试
<function call end>
test_list_append 0.010548114776611328
```

装饰器实现单实例

```
def singleton(cls, *args, **kwargs):
    instance = {}
    def _singleton(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]
    return _singleton

@singleton
class S3(object):
    def __init__(self):
        pass

aa = S3()
bb = S3()
print(id(aa) == id(bb)) # True
```



**类装饰器**

对装饰器的类实现唯一要求是它必须能如函数一般使用，也就是说它必须是可调用的。所以，如果想这么做这个类必须实现`__call__`方法

```
class Decorators(object):
    """
    Usage::
        @decorator(xx="xx")  类装饰器初始化参数  通过call 执行函数
        def func(...):pass
    """
    _func_impls = {}

    def __init__(self, fd, **kwargs):
        self.fd = fd    # 装饰器参数

    def __call__(self, func):
        if self.fd:
            name = "%s.%s" % (name, str(self.fd))
        self._func_impls[name] = func
        return self._exec_func(func)

    def _exec_func(self, func):
        def truck(*args, **kwargs):
            fn_id = func.__module__ + "." + func.__name__
            if fn_id not in self._func_impls:
                fn_id = fn_id + "." + self.fd
            fn = self._func_impls[fn_id]
            return fn(*args, **kwargs)   # 返回
        return truck    # 闭包
```

通过描述符将类装饰器运用到类的方法上 

```
class Timeit(object):
    def __init__(self, func):
        self.func = func
    def __call__(self, *args, **kws):
        pass
    def __get__(self, instance, owner):
        return lambda *args, **kwargs: self.func(instance, *args, **kwargs)

class A(object):
    @Timeit
    def func(self,a=2):
        return 2+a
```

