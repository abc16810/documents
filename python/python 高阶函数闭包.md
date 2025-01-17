#### python 高阶函数闭包及装饰器

函数式编程已经席卷了软件开发领域。这个概念并不新鲜，它早于我们所知的高级编程语言的出现，其根源是lambda演算。在Lambda演算中，有一些函数具有“自由变量”，这意味着它们使用的变量不是作为直接参数传递给它们的。带有自由变量的函数在本例中称为“闭包”。

闭包(closure)是函数式编程的重要的语法结构。闭包也是一种组织代码的结构，它同样提高了代码的可重复使用性。
当一个内嵌函数引用其外部作作用域的变量,我们就会得到一个闭包. 总结一下,创建一个闭包必须满足以下几点:

- 必须有一个内嵌函数
- 内嵌函数必须引用外部函数中的变量
- 外部函数的返回值必须是内嵌函数

#### 闭包

函数是一个对象，所以可以作为某个函数的返回结果

```
def fun1():
    def fun2(x):
        return 2*x+1
    return fun2
    
f=fun1()
print(f(5)) # 11
```

上面的代码可以成功运行。fun1的返回结果被赋给fun2对象。上面的代码将打印11。

一个函数和它的环境变量合在一起，就构成了一个闭包(closure)。在Python中，所谓的闭包是一个包含有环境变量取值的函数对象。环境变量取值被保存在函数对象的`__closure__`属性中。比如下面的代码：

```
def fun1():
	b = 10
    def fun2(x):
        return 2*x+b
    return fun2
    
f=fun1()
print(f.__closure__) # (<cell at 0x0000016FF090B4C0: int object at 0x00007FF9797B1830>,)
print(f.__closure__[0].cell_contents) # 10
print(f(5))
```

`__closure__`里包含了一个元组(tuple)。这个元组中的每个元素是cell类型的对象。我们看到第一个cell包含的就是整数10，也就是我们创建闭包时的环境变量b的取值。

#### 返回结果为函数

闭包可以看作是高阶函数的一个特殊例子，它接收一些参数作为输入，它的返回结果本身就是一个函数，可以像其他变量一样使用和传递。

```
def cons(a, b):
    def pair(f):
        return f(a, b)
    return pair
# 函数是一个对象，所以可以作为某个函数的返回结果
>>> my = cons(1,2)
>>> my
<function pair at 0x7fbb45480578>
# my 接受一个函数参数，并返回执行fun(a,b)的结果
my = cons(1,2)
print(my(lambda x,y: x+y))  # 3

def maxOfTwo(a,b):
    if a >= b:
        return a
    else:
        return b

my = cons(1,2)
# 在函数编程（FP）中，一个函数可以接收其他函数，并将它们作为正常值传递
print(my(maxOfTwo))  # 2
```
在我们的示例问题中，内部函数pair是一个闭包，因为它使用了在外部范围(在cons级别)定义的变量a和b。

### 装饰器

装饰器(decorator)是一种高级Python语法。装饰器可以对一个函数、方法或者类进行加工。在Python中，我们有多种方法对函数和类进行加工，比如在Python闭包中，我们见到函数对象作为某一个函数的返回结果。相对于其它方式，装饰器语法简单，代码可读性高。因此，装饰器在Python项目中有广泛的应用。


用装饰器对上述代码修改如下
```
def cons_decorator(F):
    def new_F(a,b):
        return F(a,b)
    return new_F

# get first
@cons_decorator
def car(a,b):
    return a
 
# get second
@cons_decorator
def cdr(a,b):
    return b
    
>>> print(car(1,2))
1
>>> print(cdr(1,2))
2
```
装饰器可以用def的形式定义，如上面代码中的decorator。装饰器接收一个可调用对象作为输入参数，并返回一个新的可调用对象。装饰器新建了一个可调用对象，也就是上面的new_F。并通过调用F(a, b)来实现原有函数的功能。
定义好装饰器后，我们就可以通过@语法使用 了。在函数car和cdr定义之前调用@cons_decorator，我们实际上car和cdr 传递给cons_decorator，并将cons_decorator返回的新的可调用对象赋给原来的函数名(car和cdr)。 所以，当我们调用cdr(3, 4)的时候，就相当于：
```
cdr=cons_decorator(cdr)
cdr(3,4)
```


### 闭包的应用

如果要编写惰性求值（lazy evaluation）或延迟求值的代码，闭包和嵌套函数特别有用
例如：
```
def page(url):
    def get():
        return urlopen(url).read()
    return get
```
在这个例子中， page()函数实际上并不执行任何有意义的计算。相反，它只会创建和返回函数get()，调用改函数的时会获取Web页面的内容。因此，get()函数中的执行的计算实际上延迟到了程序后面对get()求值的时候。
```
test1 = page('http://www.baidu.com')
test2 = page('http://www.sign.com')
test1()
```

如果需要在一系列函数调用中保持某个状态，使用闭包是一种非常高效的方式，一个简单的计数器的代码：
```
>>> def a(n):
...  def b():
...   nonlocal n
...   r = n
...   n -= 1
...   return r
...  return b
```
next（） 获取下一个值
```
>>> next = a(100)
>>> while True:
...  v = next()
...  if not v: break
```