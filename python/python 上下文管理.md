**contextlib**模块包含了与上下文管理器和with声明相关的工具。通常如果你想写一个上下文管理器，则你需要定义一个类包含`__enter__`方法以及`__exit__`方法，从而实现自定义上下文管理器

```
class ListTransaction(object):

    def __init__(self, l):
        self.l = l

    def __enter__(self):
        self.f = list(self.l)
        return self.f
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.l[:] = self.f
        return False

items = [1,2,3]
with ListTransaction(items) as working:
    working.append(5)
    working.append('a')
print(items)
# 输出  [1, 2, 3, 5, 'a']
```

> 这个类支持对已有列表进行一系列的修改，但是这些修改只是在没有异常发生时才会生效，否则原始列表保持不变

```
try:
    with ListTransaction(items) as working:
        working.append(5)
        working.insert(0,'a')
        raise RuntimeError
except RuntimeError as f:
    pass   
print(items)
# 输出 [1, 2, 3]
```

上下文管理器被with声明所激活，这个API涉及到两个方法：

1. `__enter__`方法，当执行流进入with代码块时，`__enter__`方法将执行。并且它将返回一个可供上下文使用的对象。 所以在`__enter__`中 return
2. 当执行流离开with代码块时，`__exit__`方法被调用，它将清理被使用的资源。

如打开一个文件并读写操作

```
with open("new.txt", "w") as f:
    print(f.closed)
print(f.closed)
# 输出
<!--False-->
<!--True-->
```

> 执行with代码块的时候，文件打开，并返回一个文件句柄对象f，在代码块里执行读写操作，离开with代码块时，文件执行close() 关闭打开的文件句柄 

通过**contextlib** 我们可以定义自己的with 如下

```
@contextlib.contextmanager
def myopen(file_path, mode):
    f = open(file_path, mode, encoding="utf-8")
    try:
        yield f
    finally:
        f.close()

with myopen("new.txt", "w") as f:
    f.write("Hello World!")
```

> 看上面这个例子，函数中yield之前的所有代码都类似于上下文管理器中__enter__方法的内容。而yield之后的所有代码都如__exit__方法的内容。

计算函数的执行时间with版本

```
import time
class Demo:
    def __init__(self, value):
        self.value = value
    def __enter__(self):
        self.start = time.time()
    def __exit__(self, exc_type, exc_value, traceback):
        end = time.time()
        print("{}:{}".format(self.value, end-self.start))


@contextlib.contextmanager
def demo1(value):
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print("{}:{}".format(value, end-start))

with demo1("counting time:"):
    n = 10000000
    while n > 0:
        n -= 1
with Demo("counting time:"):
    n = 10000000
    while n > 0:
        n -= 1
```

线程池

```
@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()

pools = min(multiprocessing.cpu_count() - 1, 2)
with poolcontext(processes=pools) as pool:    
    pool.map(func, [1,2,3], 1)
```

```
from concurrent.futures import ThreadPoolExecutor
    files = glob.glob(infile)
    with ThreadPoolExecutor() as executor:
        for f in files:
            name = os.path.basename(f)
            outfile = os.path.join(outpath, name)
            run(f, outfile)
```