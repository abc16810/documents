**Threading**允许代码并行，多线程非常适合加速I/O绑定的任务，比如发起web请求、数据库操作或对文件进行读写。与这种CPU密集型任务(如数学计算任务)相比，使用`multiprocessing`的好处最大。这是由于GIL(全局解释器锁)。

从Python 3.2开始，Python在并发中引入了一个名为`ThreadPoolExecutor`的新类在`concurrent.futures`模块，有效地管理和创建线程。python已经内置了一个线程模块，那么为什么要引入一个新模块呢?

- `ThreadPoolExecutor`允许您在Python中创建和管理线程池

- 在线程数量较少的情况下，动态生成新线程不是问题，但如果要处理多个线程，则管理线程真的很麻烦。除此之外，创建这么多线程在计算上是低效的，这会导致吞吐量的下降。保持吞吐量的一种方法是预先创建并实例化一个空闲线程池，并重用这个池中的线程，直到所有线程耗尽。这样可以减少创建新线程的开销。
- 此外，池可以跟踪和管理线程的生命周期，并以程序员的名义对它们进行调度，从而使代码更简单，bug更少



#### Python线程池的需求

创建的每个线程都需要应用资源(例如用于线程堆栈空间的内存)。如果我们为特定任务反复创建和销毁许多线程，那么设置线程的计算成本可能会变得非常昂贵。相反，如果我们希望在整个程序中运行许多特别的任务，我们宁愿保留工作线程以便重用，这可以通过使用线程池来实现。

#### 什么是线程池

[thread pool](https://en.wikipedia.org/wiki/Thread_pool) 是一种用于自动管理工作线程池的编程模式，池负责固定线程的数量

- 它控制创建线程的时间，比如什么时候需要线程
- 它还控制线程在不被使用时应该做什么，比如让它们等待而不消耗计算资源

池中的每个线程都称为工作者或工作线程。每个worker与执行的任务类型无关，与执行一组类似(同构)或不同(异构)任务的线程池用户无关，这些任务涉及调用的函数、函数参数、任务持续时间等

工作线程被设计为在任务完成后可重用，并在不影响工作线程本身的情况下，提供对任务意外失败(例如引发异常)的保护，这与单个线程不同，单个线程被配置为一个特定任务的单一执行

池可以提供一些配置工作线程的工具，比如运行初始化函数，使用特定的命名约定为每个工作线程命名。线程池可以提供一个通用接口，用于执行带有可变数量参数的特别任务，但不需要我们选择一个线程来运行任务、启动线程或等待任务完成。

使用线程池比手动启动、管理和关闭线程要高效得多，特别是在有大量任务时。Python通过`ThreadPoolExecutor`类提供了一个线程池

#### ThreadPoolExecutor 

`concurrent.futures`模块在Python 3.2中被引入，由Brian Quinlan编写，它同时提供线程池和进程池，不过我们将在本指南中重点关注线程池

如果感兴趣，可以通过thread.py直接访问`ThreadPoolExecutor`类的Python源代码。在您熟悉了该类的外部工作方式之后，深入研究该类的内部工作方式可能会很有趣

`ThreadPoolExecutor`扩展了Executor类，并在调用它时返回Future对象

- Executor: `ThreadPoolExecutor`的父类，它定义了池的基本生命周期操作
- Future:向线程池提交任务时返回的对象

**Executors**

`ThreadPoolExecutor`类继承了抽象的Executor类。Executor类定义了三个用于控制线程池的方法;它们是:`submit()、map()和shutdown()`

- submit():调度一个要执行的函数并返回一个未来的对象
- map():对元素的可迭代对象应用一个函数
- shutdown():关闭执行器。

Executor在创建类时启动，必须通过调用shutdown()显式地关闭，它将释放Executor持有的任何资源。我们也可以自动关闭。

submit()和map()函数用于将任务提交给Executor以进行异步执行

map()函数的操作类似于内置的map()函数，用于将函数应用于可迭代对象(如列表)中的每个元素。与内置map()函数不同，该函数对元素的每个应用程序都将异步发生，而不是顺序发生

submit()函数接受一个函数和任何参数，并将异步执行它，尽管调用会立即返回并提供一个Future对象

**Futures**

future是表示异步任务延迟结果的对象。它有时也被称为承诺或延迟。它为可能正在执行或不正在执行的任务结果提供了上下文，并提供了在结果可用时获取结果的方法

在Python中，Future对象是从一个Executor(例如ThreadPoolExecutor)返回的，当调用submit()函数来调度一个异步执行的任务时。

一般来说，我们不创建Future对象;我们只接收它们及我们可能需要对它们调用函数。对于通过调用submit()发送到ThreadPoolExecutor的每个任务，总是有一个Future对象

Future对象提供了许多有用的函数来检查任务的状态，例如:`cancelled()、running()和done()`，以确定任务是否被取消、当前正在运行或已经完成执行

- cancelled():如果任务在执行前被取消，则返回True
- running():如果任务正在运行，则返回True。
- done():如果任务已经完成或被取消，则返回True。

无法取消正在运行的任务，而已完成的任务可能已被取消。Future对象还通过result()函数提供对任务结果的访问。如果在执行任务时引发了异常，它将在调用result()函数时重新引发，或者可以通过exception()函数访问

- result():访问运行任务的结果
- exception():访问在运行任务时引发的任何异常

result()和exception()函数都允许将timeout指定为参数，即任务尚未完成时等待返回值的秒数。如果超时过期，则会引发TimeoutError。

最后，我们可能希望线程池在任务完成后自动调用函数，这可以通过add_done_callback()函数向任务的Future对象附加一个回调来实现

- add_done_callback():向任务添加一个回调函数，在任务完成后由线程池执行

们可以为每个任务添加多个回调，它们将按照添加的顺序执行。如果任务在我们添加回调之前已经完成，那么回调将立即执行。在回调函数中引发的任何异常都不会影响任务或线程池。我们将在后面的部分更详细地研究Future对象。



既然我们已经熟悉了Executor类提供的`ThreadPoolExecutor`的功能以及通过调用submit()返回的Future对象，那么让我们仔细看看`ThreadPoolExecutor`类的生命周期

**生命周期**

`ThreadPoolExecutor`提供了一个通用工作线程池。

- **threading.Thread**:Python中的手动线程。
- **concurrency.futures.ThreadPoolExecutor**: Python中的自动或“只是工作”线程模式

在使用ThreadPoolExecutor类的生命周期中有四个主要步骤;它们是:创建、提交、等待和关闭。

- 创建:通过调用构造函数ThreadPoolExecutor()创建线程池
- 提交:通过调用Submit()或map()提交任务并获取futures 
- 等待:等待并在任务完成时获得结果(可选)
- 关闭:通过调用shutdown()关闭线程池

下图有助于描述ThreadPoolExecutor类的生命周期

![](D:\u\网站文档\img\微信截图_20220424114704.png)

**1. 创建线程池**

当ThreadPoolExecutor的实例被创建时,它必须配置固定数量的线程池中,为池中的每个线程命名时使用的前缀`thread_name_prefix`,  以及在初始化每个线程时要调用的函数名以及该函数的任何参数

创建池时，系统中每个CPU有一个线程，外加4个线程。这对于大多数目的都是好的

```
默认总线程数=(总cpu) + 4
```

例如，如果您有4个cpu，每个cpu都有超线程(大多数现代cpu都有超线程)，那么Python将看到8个cpu，并默认为池分配(8 + 4)或12个线程

```
# 使用默认工作线程数创建线程池  
executor = ThreadPoolExecutor()
# 测试应用程序以确定产生最佳性能的线程数(从几个线程到数百个线程)是一个好主意
```

拥有数千个线程通常不是一个好主意，因为它可能会开始影响可用RAM的数量，并导致线程之间的大量切换，这可能会导致更糟糕的性能。

可以通过max_workers参数指定要在池中创建的线程数;例如:

```
# 创建一个具有10个工作线程的线程池
executor = ThreadPoolExecutor(max_workers=10)
```

**2. 提交任务到线程池**

一旦创建了线程池，就可以提交任务以异步执行。

如前所述，有两种主要的方法来提交定义在Executor父类上的任务。它们是:map()和submit()。

- map()提交任务

map()函数是内置map()函数的异步版本，用于将函数应用于可迭代对象(如列表)中的每个元素。您可以在池中调用map()函数，并将您的函数名和可迭代对象传递给它

当将for循环转换为在每个循环迭代中使用一个线程运行时，您最有可能使用map()。

```
# 并行执行所有任务
results = pool.map(my_task, my_items) # does not block
# my_task是你想要执行的函数，
# my_items是你的对象的可迭代对象，每个对象都由my_task函数执行
```

任务将在线程池中排队，并在可用时由线程池中的工作线程执行。

map()函数将立即返回一个可迭代对象。这个可迭代对象可用于访问目标任务函数的结果，因为它们是按照任务提交的顺序提供的(例如，你提供的可迭代对象的顺序)。

```
# 在结果可用时迭代它们
for result in executor.map(my_task, my_items):
	print(result) 
	
```

在调用map()时，如果您希望限制在迭代过程中等待每个任务完成的时间，您还可以通过“timeout”参数设置超时，以秒为单位，在此之后将引发timeout错误。

```
# 并行执行所有任务
# 在结果可用时迭代它们
for result in executor.map(my_task, my_items, timeout=5):
	# 等待任务完成或超时
	print(result)
	
```

- Submit()提交任务

submit()函数将一个任务提交给线程池执行。该函数接受要调用的函数名和函数的所有参数，然后立即返回一个Future对象

Future对象承诺返回任务的结果(如果有的话)，并提供了一种确定特定任务是否已经完成的方法

```
# 提交一个带参数的任务并获取一个future object
future = executor.submit(my_task, arg1, arg2) # does not block
#my_task是你想要执行的函数，arg1和arg2是传递给my_task函数的第一个和第二个参数
```

也可以使用submit()函数来提交不带任何参数的任务;例如

```
# 提交一个不带参数的任务并获取一个future对象
future = executor.submit(my_task) # does not block
```

可以通过返回的Future对象的result()函数访问任务的结果。此调用将阻塞，直到任务完成

```
# 从future得到结果
result = future.result() # blocks
```

同样如果您希望限制您愿意等待每个任务完成的时间，您还可以在调用result()时通过" timeout "参数设置超时，以秒为单位，在此之后将引发timeout错误。

```
# 等待任务完成或超时
result = future.result(timeout=5) # blocks
```

**3. 等待任务完成(可选)**

`concurrent.futures`模块提供了两个模块实用函数，通过它们的Future对象等待任务

Future对象仅在调用submit()将任务推入线程池时创建

这些等待函数是可选的，因为您可以在调用map()或submit()之后直接等待结果，或者等待线程池中的所有任务完成。这两个模块函数分别是wait()用于等待Future对象完成，以及as_completed()用于在任务完成时获取Future对象

- wait():等待一个或多个Future对象，直到它们完成。
- as_completed():当Future对象完成执行时，从集合中返回它们

您可以将这两个函数与一个或多个线程池创建的Future对象一起使用，它们并不特定于应用程序中的任何给定线程池。如果您希望跨执行不同类型任务的多个线程池执行等待操作，那么这将非常有用

这两个函数都适用于通过列表压缩中的提交将多个任务分派到线程池的习惯用法;例如

```
# 将任务分派到线程池中，并创建一个futures列表 
futures = [executor.submit(my_task, my_data) for my_data in my_datalist]
# 这里，my_task是我们的自定义目标任务函数，my_data是作为参数传递给my_task的数据的一个元素，“my_datalist”是我们的my_data对象的源
```

然后可以将Future对象传递给wait()或as_completed()

以这种方式创建Future对象列表不是必需的，只是将for循环转换为提交给线程池的任务时的一种常见模式

**3.1 等待Futures 直到完成**

wait()函数可以接受一个或多个Future对象，并将在指定操作发生时返回，例如所有任务完成、一个任务完成或一个任务引发异常

该函数将返回一组Future对象，它们与通过`return_when`函数设置的条件相匹配。第二个集合将包含不满足条件的任务的所有futures 。它们被称为“done”和“not_done” futures集合

这对于等待大量的工作是有用的，当我们得到第一个结果时就停止等待

这可以通过传递给“return_when”参数的FIRST_COMPLETED常量来实现

```
# 等待直到得到第一个结果
done, not_done = wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
```

或者，我们可以通过ALL_COMPLETED常量等待所有任务完成。如果您正在使用submit()来分派任务，并且正在寻找一种简单的方法来等待所有工作完成，那么这可能会很有帮助。

```
# 等待所有任务完成
done, not_done = wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
```

还有一个选项可以通过FIRST_EXCEPTION常量等待第一个异常

```
# 等待第一个异常
done, not_done = wait(futures, return_when=concurrent.futures.FIRST_EXCEPTION)
```

**3.2 等待Futures 完成**

并发执行任务的美妙之处在于，我们可以在它们可用时获得结果，而不是等待所有任务完成。

当任务在线程池中完成时，[as_completed()](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.as_completed)函数将为任务返回Future对象

我们可以调用该函数，并向它提供通过调用submit()创建的Future对象列表，它将在Future对象以任何顺序完成时返回它们

通常使用as_completed()函数循环遍历在调用submit时创建的Future对象列表;例如

```
# 遍历所有提交的任务并获得可用的结果  
for future in as_completed(futures):
	# 获取下一个已完成任务的结果
	result = future.result() # blocks
```

注： 这与以第两种方式迭代调用map()的结果不同。首先，map()返回对象的迭代器，而不是Future对象。其次，map()按照任务提交的顺序返回结果，而不是按照任务完成的顺序

**关闭线程池**

一旦所有任务完成，我们可以关闭线程池，这将释放每个线程和它可能持有的任何资源(例如线程堆栈空间)

```
# 关闭线程池
executor.shutdown() # blocks
```

默认情况下，shutdown()函数将等待线程池中的所有任务完成后返回

这种行为可以通过在调用shutdown()时将" wait "参数设置为False来改变，在这种情况下函数将立即返回。线程池使用的资源将不会被释放，直到所有当前和排队的任务完成

```
# 关闭线程池
executor.shutdown(wait=False) # does not blocks
```

我们还可以指示池取消所有排队的任务，以防止它们执行。这可以通过将`cancel_futures`参数设置为True来实现。默认情况下，当调用shutdown()时，队列任务不会被取消

```
# 取消所有队列任务 （python3.9）
executor.shutdown(cancel_futures=True) # blocks
```

如果我们忘记关闭线程池，线程池将在我们退出主线程时自动关闭。如果我们忘记关闭池，而仍然有任务在执行，主线程将不会退出，直到池中的所有任务和所有排队的任务都执行完毕。

#### ThreadPoolExecutor上下文管理器

使用ThreadPoolExecutor类的首选方法是使用上下文管理器。这与处理其他资源(如文件和套接字)的首选方式相匹配

使用带有上下文管理器的ThreadPoolExecutor涉及到使用“with”关键字创建一个块，您可以在其中使用线程池来执行任务和获取结果

一旦块完成，线程池将自动关闭。在内部，上下文管理器将使用默认参数调用shutdown()函数，等待所有排队和正在执行的任务在返回和继续之前完成。

```
# 创建线程池
with ThreadPoolExecutor(max_workers=10) as pool:
	# 提交任务并获得结果
	# ...
	# 自动关闭线程池…
# 此时池已关闭
```

如果要将for循环转换为多线程，这是一个非常方便的习惯用法

如果您希望线程池在后台操作，而您在程序的主线程中执行其他工作，或者希望在整个程序中多次重用线程池，那么它就不那么有用了

#### ThreadPoolExecutor例子

ThreadPoolExecutor最常见的用例可能是从互联网上并发地下载文件

这是一个很有用的问题，因为我们有很多方法可以下载文件。我们将以这个问题为基础，探讨使用ThreadPoolExecutor并发下载文件的不同模式

**连续的下载文件**

考虑这样一种情况，我们可能需要一些关于并发性的Python API文档的本地副本，以便稍后查看。我们可能需要下载以下10个url的本地副本，它们涵盖了Python并发性api的范围。我们可以将这些url定义为字符串列表，以便在程序中进行处理

```
# python concurrency API docs
URLS = ['https://docs.python.org/3/library/concurrency.html',
        'https://docs.python.org/3/library/concurrent.html',
        'https://docs.python.org/3/library/concurrent.futures.html',
        'https://docs.python.org/3/library/threading.html',
        'https://docs.python.org/3/library/multiprocessing.html',
        'https://docs.python.org/3/library/multiprocessing.shared_memory.html',
        'https://docs.python.org/3/library/subprocess.html',
        'https://docs.python.org/3/library/queue.html',
        'https://docs.python.org/3/library/sched.html',
        'https://docs.python.org/3/library/contextvars.html']
```

在Python中下载url相当容易。首先，我们可以尝试使用urllib.request.urlopen()函数打开到服务器的连接，并指定URL和以秒为单位的合理超时

这将提供一个连接，然后我们可以调用read()函数来读取文件的内容。对连接使用上下文管理器将确保它将自动关闭，即使出现异常

下面的download_url()函数实现了这一点，它以URL作为参数并返回文件的内容，如果由于任何原因无法下载文件，则返回None。我们将设置一个漫长的超时3秒，以防我们的网络连接出现问题

```
def download_url(url):
    try:
        # open a connection to the server
        with urlopen(url, timeout=3) as connection:
            # read the contents of the html doc
            return connection.read()
    except:
        # bad url, socket timeout, http forbidden, etc.
        return None
```

一旦有了URL的数据，就可以将其保存为本地文件。

首先，我们需要检索URL中指定的文件的文件名。有几种方法可以做到这一点，但在处理路径时，`os.path.basename()`函数是一种常见的方法。然后，我们可以使用`os.path.join()`函数，使用指定的目录和文件名来构造用于保存文件的输出路径

然后，我们可以使用open()内置函数以写二进制模式打开文件，并保存文件的内容，再次使用上下文管理器确保在完成操作后关闭文件

最后用下面的save_file()函数实现了这一点，它获取已下载的URL、已下载文件的内容以及我们希望保存已下载文件的本地输出路径。它返回用于保存文件的输出路径，以防我们想要向用户报告进度。

```
# 保存为本地文件
def save_file(url, data, path):
    filename = basename(url)
    outpath = join(path, filename)
    with open(outpath, 'wb') as file:
        file.write(data)
    return outpath
```

接下来，我们可以针对列表中的给定URL调用download_url()函数，然后调用save_file()来保存每个下载的文件

下面的download_and_save()函数实现了这一点，它会报告整个过程，并处理无法下载url的情况。

```
# 下载url并将其保存为本地文件
def download_and_save(url, path):
    data = download_url(url)
    if data is None:
        print(f'>Error downloading {url}')
        return
    outpath = save_file(url, data, path)
    print(f'>Saved {url} to {outpath}')
```

最后，我们需要一个函数来驱动这个过程

首先，如果保存文件的本地输出位置不存在，则需要创建它。我们可以使用`os.makedirs()`函数来实现这一点

我们可以遍历url列表，并为每个url调用download_and_save()函数

```
def download_docs(urls, path):
    # 如果需要，创建本地目录
    makedirs(path, exist_ok=True)
    for url in urls:
        download_and_save(url, path)
```

综上，下面列出了连续下载文件的完整示例

```
# download document files and save to local files serially
from os import makedirs
from os.path import basename
from os.path import join
from urllib.request import urlopen
 

def download_url(url):
    try:
        with urlopen(url, timeout=3) as connection:
            return connection.read()
    except:
        # 错误的url，套接字超时，HTTP被禁止，等等.
        return None
 

def save_file(url, data, path):
    filename = basename(url)
    outpath = join(path, filename)
    with open(outpath, 'wb') as file:
        file.write(data)
    return outpath
 

def download_and_save(url, path):
    data = download_url(url)
    if data is None:
        print(f'>Error downloading {url}')
        return
    outpath = save_file(url, data, path)
    print(f'>Saved {url} to {outpath}')
 

def download_docs(urls, path):
    makedirs(path, exist_ok=True)
    for url in urls:
        download_and_save(url, path)
 
# python concurrency API docs
URLS = ['https://docs.python.org/3/library/concurrency.html',
        'https://docs.python.org/3/library/concurrent.html',
        'https://docs.python.org/3/library/concurrent.futures.html',
        'https://docs.python.org/3/library/threading.html',
        'https://docs.python.org/3/library/multiprocessing.html',
        'https://docs.python.org/3/library/multiprocessing.shared_memory.html',
        'https://docs.python.org/3/library/subprocess.html',
        'https://docs.python.org/3/library/queue.html',
        'https://docs.python.org/3/library/sched.html',
        'https://docs.python.org/3/library/contextvars.html']
# local path for saving the files
PATH = 'docs'
# download all docs
download_docs(URLS, PATH)
```

运行该示例将遍历url列表并依次下载每个url，然后将每个文件保存到指定目录的本地文件中。

接下来，我们可以看看如何使用线程池使程序并发

#### 使用submit()同时下载文件

让我们来看看如何更新我们的程序，以便使用ThreadPoolExecutor并发地下载文件，首先想到的可能是使用map()，因为我们只是想让for循环并发。不幸的是，我们在每次循环中调用的download_and_save()函数有两个参数，其中只有一个是可迭代对象。另一种方法是使用submit()在一个单独的线程中为所提供列表中的每个URL调用download_and_save()

为此，我们可以首先配置一个线程池，使其线程数等于列表中的url数。我们将为线程池使用上下文管理器，以便在完成时为我们自动关闭它。

然后，我们可以使用列表压缩为每个URL调用submit()函数。我们甚至不需要调用submit返回的Future对象，因为我们不需要等待结果

```
n_threads = len(urls)
with ThreadPoolExecutor(n_threads) as executor:
    # 下载每个url并保存为本地文件
    _ = [executor.submit(download_and_save, url, path) for url in urls]
```

一旦每个线程完成，上下文管理器将为我们关闭线程池，任务完成

我们甚至不需要添加显式调用来等待，尽管如果我们想要使代码更具可读性，我们可以添加;例如:

```
n_threads = len(urls)
with ThreadPoolExecutor(n_threads) as executor:
    # 下载每个url并保存为本地文件
    futures = [executor.submit(download_and_save, url, path) for url in urls]
    # 等待所有下载任务完成
    _, _ = wait(futures)
```

但是，添加这种等待是不必要的。

下载和保存文件的download_docs()函数的更新版本如下所示

```
def download_docs(urls, path):
    makedirs(path, exist_ok=True)
    n_threads = len(urls)
    with ThreadPoolExecutor(n_threads) as executor:
        # 下载每个url并保存为本地文件
        _ = [executor.submit(download_and_save, url, path) for url in urls]
```

更新上述的完整实例代码，再次执行，观察执行时间，比上一个例子中连续下载所有文件所需时间的一半还少。

#### 使用submit()和as_completed()并行下载文件

也许我们想要报告下载完成的进度。
线程池允许我们通过存储调用submit()返回的Future对象，然后对Future对象集合调用as_completed()来实现这一点

另外，考虑我们在任务中正在做两件事。第一个是从远程服务器下载，这是一个io绑定操作，我们可以并发地进行。第二种是将文件的内容保存到本地硬盘，这是另一种io绑定操作，我们不能并发进行，因为大多数硬盘一次只能保存一个文件

因此，也许更好的设计是只将程序的文件下载部分作为并发任务，而将程序的文件保存部分作为串行任务

这就需要对程序进行更多的修改。我们可以为每个URL调用download_url()函数，这可以是提交给线程池的并发任务

当我们对每个Future对象调用result()时，它将给我们下载的数据，但我们不知道数据是从哪个URL下载的。Future对象不会知道，因此，我们可以更新download_url()以返回已下载的数据和作为参数提供的URL

download_url()函数的更新版本将返回一个数据元组，并在下面列出输入的URL

```
def download_url(url):
    try:
        with urlopen(url, timeout=3) as connection:
            return connection.read(), url
    except:
        return None, url
```

然后，我们可以向线程池的每个URL提交对该函数的调用，以提供一个Future对象

```
futures = [executor.submit(download_url, url) for url in urls]
```

到目前为止，一切顺利。现在，我们希望保存本地文件，并在文件下载时报告进度。这要求我们拆分download_and_save()函数，并将其移回用于驱动程序的download_docs()函数

可以通过as_completed()函数遍历Future对象，该函数将按照下载完成的顺序返回Future对象，而不是按照将它们分派到线程池的顺序

然后，我们可以从Future对象检索数据和URL

```
# 对每个结果进行可用的处理
for future in as_completed(futures):
    # 获取下载的url数据
    data, url = future.result()
```

我们可以检查下载是否不成功并报告错误，否则保存文件并正常报告进度。直接从download_and_save()函数复制粘贴

```
# 检查数据
if data is None:
    print(f'>Error downloading {url}')
    continue
outpath = save_file(url, data, path)
print(f'>Saved {url} to {outpath}')
```

download_docs()函数的更新版本只会同时下载文件，然后在文件被下载时连续保存文件

```
def download_docs(urls, path):
    makedirs(path, exist_ok=True)
    n_threads = len(urls)
    with ThreadPoolExecutor(n_threads) as executor:
        futures = [executor.submit(download_url, url) for url in urls]
        for future in as_completed(futures):
            data, url = future.result()
            if data is None:
                print(f'>Error downloading {url}')
                continue
            outpath = save_file(url, data, path)
            print(f'>Saved {url} to {outpath}')
```

更新上述的完整实例代码，运行程序后，文件会像以前一样下载并保存，可能会快几毫秒，看看程序的输出，我们可以看到保存文件的顺序是不同的

更小的文件，如`sched.html`，几乎是最后分发的，下载得更快(例如，下载的字节更少)，反过来又更快地保存到本地文件

这证实了我们确实是按照任务完成的顺序而不是任务提交的顺序来处理下载的

#### ThreadPoolExecutor使用模式

ThreadPoolExecutor为在Python中执行并发任务提供了很大的灵活性。尽管如此，还是有一些适用于大多数程序场景的通用使用模式

本节列出了常用的使用模式和工作示例，您可以将它们复制并粘贴到您自己的项目中，并根据需要进行调整

我们将看到的模式如下所示

- Map and Wait Pattern
- Submit and Use as Completed Pattern
- Submit and Use Sequentially Pattern
- Submit and Use Callback Pattern
- Submit and Wait for All Pattern
- Submit and Wait for First Pattern

我们将在每个例子中使用一个人为的任务，该任务将随机睡眠时间少于一秒。您可以在每个模式中轻松地将这个示例任务替换为您自己的任务

另外，回想一下，每个Python程序在默认情况下都有一个线程，称为主线程，我们在主线程中执行工作。在每个示例中，我们将在主线程中创建线程池，并可能在某些模式中引用主线程中的操作，而不是线程池中线程中的操作

**Map and Wait Pattern**

使用ThreadPoolExecutor时最常见的模式可能是将对集合中的每个项执行函数的for循环转换为使用线程

它假设函数没有副作用，这意味着它不会访问函数之外的任何数据，也不会更改提供给它的数据。它获取数据并产生结果

这些类型的for循环可以用Python显式编写;例如:

```
# 将函数应用于集合中的每个元素
for item in mylist:
	result = task(item)
```

更好的做法是使用内置的map()函数，该函数将该函数应用于可迭代对象中的每一项

```
results = map(task, mylist)
```

在迭代结果之前，不会对每一项执行task()函数，这就是所谓的惰性求值

```
# 迭代来自map的结果
for result in results:
	print(result)
```

因此，通常将这一操作合并为以下内容

```
for result in map(task, mylist):
	print(result)
```

我们可以使用线程池执行相同的操作，只是该函数对列表中的项的每个应用程序都是异步执行的任务。例如

```
for result in executor.map(task, mylist):
	print(result)
```

尽管任务是并发执行的，但结果是按照提供给map()函数的可迭代对象的顺序迭代的，与内置map()函数相同。

这样，我们可以将map()的线程池版本看作map()函数的并发版本，如果您希望更新for循环以使用线程，那么它是理想的

下面的示例演示了如何使用map和wait模式来处理一个任务，该任务将随机休眠少于一秒的时间，并返回所提供的值

```
#ThreadPoolExecutor的映射和等待模式的示例  
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
 
# 休眠时间可变的自定义任务  
def task(name):
    # 睡眠时间不要超过一秒钟
    sleep(random())
    return name
 
with ThreadPoolExecutor(10) as executor:
    # 并发执行任务并按顺序处理结果  
    for result in executor.map(task, range(10)):
        print(result)
```

运行这个示例，我们可以看到结果是按照创建任务并将其发送到线程池的顺序报告的

```
0
1
2
3
4
5
6
7
8
9
```

map()函数通过向map()调用提供多个可迭代对象作为参数来支持接受多个参数的目标函数。
例如，可以为map定义一个目标函数，它接受两个参数，然后为map的调用提供两个长度相同的可迭代对象

```
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
# 使用两个可迭代对象调用map的示例


def task(value1, value2):
    sleep(random())
    return value1, value2
 
with ThreadPoolExecutor() as executor:
    for result in executor.map(task, ['1', '2', '3'], ['a', 'b', 'c']):
        print(result)
```

行该示例按预期执行任务，提供两个参数来映射，并报告一个合并了两个参数的结果

```
('1', 'a')
('2', 'b')
('3', 'c')
```

对map函数的调用将立即将所有任务发送到线程池，即使您没有迭代结果的可迭代对象。
这与内置的map()函数不同，后者是惰性的，只有在迭代期间请求结果时才计算每次调用。

下面的示例通过使用map发布所有任务而不迭代结果来确认这一点

```
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
# 调用map而不迭代结果的示例


def task(value):
    sleep(random())
    print(f'Done: {value}')
    return value

# start the thread pool
with ThreadPoolExecutor() as executor:
    executor.map(task, range(5))
print('All done!')
```

运行这个示例，我们可以看到任务被发送到线程池并执行，而不必显式地传递返回结果的可迭代对象。

上下文管理器的使用确保线程池在所有任务完成之前不会关闭

```
Done: 1
Done: 3
Done: 4
Done: 0
Done: 2
All done!
```

**Submit and Use as Completed**

在使用ThreadPoolExecutor时，第二种最常见的模式可能是提交任务并在结果可用时使用它们。

这可以通过使用submit()函数来实现，将任务推入返回Future对象的线程池，然后调用Future对象列表上的模块方法as_completed()，该方法将在任务完成时返回每个Future对象

下面的示例演示了这个模式，按照从0到9的顺序提交任务，并按照完成任务的顺序显示结果

```
# ThreadPoolExecutor的提交和使用as completed模式的示例  
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

def task(name):
    sleep(random())
    return name
 
# start the thread pool
with ThreadPoolExecutor(10) as executor:
    # 提交任务并收集futures
    futures = [executor.submit(task, i) for i in range(10)]
    # 在任务结果可用时处理它们
    for future in as_completed(futures):
        print(future.result())
```

行这个示例，我们可以看到检索和打印结果的顺序是按照任务完成的顺序，而不是按照任务提交给线程池的顺序

```
8
2
6
4
9
0
1
5
3
7
```

**Submit and Use Sequentially**

我们可以按照任务提交的顺序得到任务的结果。这可能是因为任务有一个自然的顺序

我们可以通过对每个任务调用submit()来获得Future对象列表，然后按照任务提交的顺序遍历Future对象并检索结果来实现这个模式

与“as completed”模式的主要区别在于，我们直接枚举了futures 列表，而不是调用as_completed()函数

```
# 按照任务提交的顺序处理任务  
for future in futures:
	print(future.result())
```

下面的示例演示了这个模式，按照从0到9的顺序提交任务，并按照提交的顺序显示结果

```
# ThreadPoolExecutor的提交和使用顺序模式的示例  
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
 
def task(name):
    sleep(random())
    return name
 
with ThreadPoolExecutor(10) as executor:
    futures = [executor.submit(task, i) for i in range(10)]
    # 按照任务提交的顺序处理任务结果  
    for future in futures:
        print(future.result())
```

运行这个示例，我们可以看到检索和打印结果的顺序是按照任务提交的顺序，而不是按照任务完成的顺序

```
0
1
2
3
4
5
6
7
8
9
```

**Submit and Use Callback**

一旦结果可用，我们可能不想显式地处理它们;相反，我们想要对结果调用一个函数。
不像上面的as completed模式那样手动执行此操作，我们可以让线程池自动调用该函数并返回结果

这可以通过调用add_done_callback()函数并传递函数名来设置每个Future对象的回调来实现。

然后，线程池将在每个任务完成时调用回调函数，并为该任务传入Future对象

下面的示例演示了这个模式，注册了一个自定义回调函数，以便在每个任务完成时应用到它。

```
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
 

def task(name):
    sleep(random())
    return name
 
# 任务完成时调用自定义回调函数  
def custom_callback(fut):
    print(fut.result())
 
with ThreadPoolExecutor(10) as executor:
    futures = [executor.submit(task, i) for i in range(10)]
    for future in futures:
        future.add_done_callback(custom_callback)
```

运行这个示例，我们可以看到结果是按照完成的顺序检索和打印的，而不是按照任务完成的顺序

```
8
0
5
9
1
4
3
2
6
7
```

我们可以在每个Future对象上注册多个回调函数;它不局限于单个回调。调用回调函数的顺序是按照它们在每个Future对象上注册的顺序

```
...
def custom_callback1(fut):
    print(f'Callback 1: {fut.result()}')

def custom_callback2(fut):
    print(f'Callback 2: {fut.result()}')
    

with ThreadPoolExecutor(10) as executor:
    futures = [executor.submit(task, i) for i in range(10)]
    for future in futures:
        future.add_done_callback(custom_callback1)
        future.add_done_callback(custom_callback2)
```

运行这个示例，我们可以看到结果是按照任务完成的顺序报告的，每个任务调用两个回调函数的顺序是按照我们向每个Future对象注册它们的顺序报告的

**Submit and Wait for All**

通常是提交所有任务，然后等待线程池中的所有任务完成。
当任务不直接返回结果时，例如每个任务像文件一样直接将结果存储在资源中，这种模式可能很有用

有两种方法可以等待任务完成:调用wait()模块函数或调用shutdown()

最可能的情况是，您希望显式地等待线程池中的任务集或任务子集完成。
您可以通过将任务列表传递给wait()函数来实现这一点，默认情况下，该函数将等待所有任务完成

```
# 等待所有任务完成
wait(futures)
```

通过将参数" return_when "设置为ALL_COMPLETED常量，可以显式指定等待所有任务;例如

```
wait(futures, return_when=ALL_COMPLETED)
```

下面的示例演示了这个模式。请注意，我们有意忽略调用wait()的返回，因为在这种情况下我们不需要检查它

```
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait

def task(name):
    sleep(random())
    print(name)
 
with ThreadPoolExecutor(10) as executor:
    futures = [executor.submit(task, i) for i in range(10)]
    # 等待所有任务完成
    wait(futures)
    print('All tasks are done!')
```

运行这个示例，我们可以看到每个任务在任务完成时处理结果。重要的是，我们可以看到主线程一直等到所有任务都完成后才继续打印消息。

```
0
1
2
3
4
5
6
7
8
9
All tasks are done!
```

另一种方法是关闭线程池，等待所有正在执行和排队的任务完成，然后再继续。
当没有Future对象列表或只打算为一组任务使用一次线程池时，这可能是首选的

我们可以使用上下文管理器来实现这个模式;例如:

```
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
 
def task(name):
    sleep(random())
    print(name)

with ThreadPoolExecutor(10) as executor:
    futures = [executor.submit(task, i) for i in range(10)]
    # 等待所有任务完成
print('All tasks are done!')
```

我们可以在不使用上下文管理器和显式调用shutdown的情况下达到相同的效果

```
# 等待所有任务完成并关闭池  
executor.shutdown()
```

记住，shutdown()函数默认情况下会等待所有任务完成，不会取消任何排队的任务，但我们可以通过将" wait "参数设置为True，将" cancel_futures "参数设置为False来显式地实现这一点;例如

```
executor.shutdown(wait=True, cancel_futures=False)  # 默认
```

面的示例演示了通过调用shutdown()等待线程池中的所有任务完成后再继续执行的模式

```
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
 
def task(name):
    sleep(random())
    print(name)
 
executor = ThreadPoolExecutor(10)
futures = [executor.submit(task, i) for i in range(10)]
#等待所有任务完成
executor.shutdown()
print('All tasks are done!')
```

运行这个示例，我们可以看到，所有任务在完成时都会报告结果，主线程直到所有任务完成并且线程池关闭时才会继续运行

**Submit and Wait for First**

通常会发出许多任务，但只关心返回的第一个结果。也就是说，不是第一个任务的结果，而是任何恰巧是第一个完成任务执行的任务的结果

如果您试图从多个位置(如文件或数据)访问相同的资源，可能会出现这种情况

这个模式可以通过wait()模块函数实现，并将`return_when`参数设置为FIRST_COMPLETED常量。

```
# 等待任何任务完成  
done, not_done = wait(futures, return_when=FIRST_COMPLETED)
```

我们还必须手动管理线程池，方法是构造线程池并手动调用shutdown()，这样我们就可以继续执行主线程，而不必等待所有其他任务完成

下面的示例演示了该模式，并将在第一个任务完成后停止等待

```
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
from concurrent.futures import FIRST_COMPLETED
 

def task(name):
    sleep(random())
    return name
 
executor = ThreadPoolExecutor(10)
futures = [executor.submit(task, i) for i in range(10)]
# 等待任何任务完成
done, not_done = wait(futures, return_when=FIRST_COMPLETED)
# 从第一个要完成的任务中获取结果  
print(done.pop().result())
# 关闭不等待其它其它任务完成
executor.shutdown(wait=False, cancel_futures=True)
```

运行该示例将等待任何任务完成，然后检索第一个完成任务的结果并关闭线程池。重要的是，任务将继续在后台的线程池中执行，主线程直到所有任务完成才会关闭

#### 如何配置ThreadPoolExecutor

我们可以在构造ThreadPoolExecutor实例时定制线程池的配置。
我们可能希望为应用程序定制线程池的三个方面;它们是工作线程的数量、池中线程的名称以及池中每个线程的初始化。

**配置线程数**

线程池中的线程数可以通过`max_workers`参数配置

接受一个正整数，默认为系统中cpu的数量加上4

```
max_workers = min(32, (os.cpu_count() or 1) + 4)  # python3.8 
max_workers = (os.cpu_count() or 1) * 5   # python3.6
```

例如，如果您的系统中有2个物理CPU，每个CPU都有超线程(在现代CPU中很常见)，那么您将有2个物理CPU和4个逻辑CPU。Python会看到4个cpu。系统上的默认工作线程数是(4 + 4)或8

如果这个数字大于32(例如，16个物理核、32个逻辑核，再加上4个)，默认将上限设置为32个线程

在您的系统中，线程通常多于cpu(物理或逻辑)。这是因为线程用于io绑定的任务，而不是cpu绑定的任务。这意味着线程用于等待相对较慢的资源响应的任务，如硬盘驱动器、DVD驱动器、打印机和网络连接等。我们将在后面一节讨论线程的最佳应用程序。

因此，应用程序中有数十、数百甚至数千个线程并不罕见，这取决于您的特定需求。有超过一千或几千个线程是不寻常的。如果您需要这么多线程，那么可能首选替代解决方案，例如AsyncIO。我们将在后面的章节中讨论线程vs. AsyncIO

首先，让我们检查在您的系统上为线程池创建了多少线程。下面的示例报告系统上线程池中的默认线程数。

```
# 报告系统上的默认工作线程数 
from concurrent.futures import ThreadPoolExecutor
# 使用默认工作线程数创建线程池  
pool = ThreadPoolExecutor()
print(pool._max_workers)
```

我们可以直接指定工作线程的数量，这在大多数应用程序中都是一个好主意。下面的例子演示了如何配置500个工作线程

```
from concurrent.futures import ThreadPoolExecutor
pool = ThreadPoolExecutor(500)
print(pool._max_workers)
```

**应该使用多少线程**

如果您有数百个任务，您可能应该将线程的数量设置为与任务的数量相等。如果您有数千个任务，那么可能应该将线程数限制在数百或1000。如果您的应用程序打算在将来多次执行，您可以测试不同数量的线程并比较总体执行时间，然后选择能够提供最佳性能的线程数量。您可能希望使用随机睡眠操作来模拟这些测试中的任务。

**配置线程名称**

Python中的每个线程都有一个名称。
主线程的名字是`MainThread`。您可以通过调用threading模块中的main_thread()函数来访问主线程，然后访问name成员。例如

```
from threading import main_thread
thread = main_thread()
print(thread.name)   # MainThread
```

默认情况下，名称是唯一的。
这在调试具有多个线程的程序时很有帮助。日志消息可以报告正在执行特定步骤的线程，或者可以使用调试来跟踪具有特定名称的线程

在线程池中创建线程时，每个线程都有一个名称“ThreadPoolExecutor-%d_%d”，其中第一个%d表示线程池号，第二个%d表示线程号，这两个名称都是按照线程池和线程创建的顺序排列的。

如果我们在分配一些工作之后直接访问池中的线程，以便创建所有线程，就可以看到这一点。

我们可以通过threading模块中的enumerate()函数枚举Python程序(进程)中的所有线程，然后报告每个线程的名称。
下面的示例使用默认的线程数创建一个线程池，将工作分配给该池以确保创建了线程，然后报告程序中所有线程的名称

```
import threading
from concurrent.futures import ThreadPoolExecutor
 
# 什么都不做的模拟任务
def task(name):
    pass
 
executor = ThreadPoolExecutor()
executor.map(task, range(10))
for thread in threading.enumerate():
    print(thread.name)
executor.shutdown()
```

运行该示例将报告系统中所有线程的名称，首先显示主线程的名称和池中四个线程的名称。
在本例中，由于任务执行得太快，只创建了4个线程。回想一下，工作线程是在它们完成任务之后使用的。重用工作者的能力是使用线程池的一个主要好处

```
MainThread
ThreadPoolExecutor-0_0
ThreadPoolExecutor-0_1
ThreadPoolExecutor-0_2
ThreadPoolExecutor-0_3
```

“ThreadPoolExecutor-%d”是线程池中所有线程的前缀，我们可以为它定制一个名称，这个名称可能在应用程序中对线程池执行的任务类型有意义

线程名前缀可以在构造线程池时通过`thread_name_prefix`参数设置。

下面的示例将前缀设置为“TaskPool”，它前缀为在池中创建的每个线程的名称

```
import threading
from concurrent.futures import ThreadPoolExecutor
 
def task(name):
    pass
 
# 使用自定义名称前缀创建线程池 
executor = ThreadPoolExecutor(thread_name_prefix='TaskPool')
executor.map(task, range(10))
for thread in threading.enumerate():
    print(thread.name)
executor.shutdown()
```

运行该示例会像前面一样报告主线程的名称，但在本例中，报告的是线程池中带有自定义线程名称前缀的线程名称

```
MainThread
TaskPool_0
TaskPool_1
TaskPool_2
TaskPool_3
```

**配置初始化**

工作线程可以在开始处理任务之前调用函数。
这被称为初始化器函数，可以在创建线程池时通过**initializer**参数指定(python3.7)。如果初始化器函数接受参数，它们可以通过`initargs`参数传递给线程池，线程池是传递给初始化器函数的参数元组

默认情况下，没有初始化器函数。如果希望每个线程设置特定于该线程的资源，可以选择为工作线程设置初始化器函数

示例可能包括特定于线程的日志文件或到远程资源(如服务器或数据库)的特定于线程的连接。然后，该资源将对该线程执行的所有任务可用，而不是为每个任务创建和丢弃或打开和关闭。

这些线程特定的资源可以存储在工作线程可以引用的地方，比如全局变量，或者线程局部变量。在完成线程池之后，必须小心正确地关闭这些资源。

下面的示例将创建一个具有两个线程的线程池，并使用自定义初始化函数。在这种情况下，这个函数除了打印工作线程名之外什么也不做。然后使用线程池完成10个任务

```
from time import sleep
from random import random
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor
 
# 用于初始化工作线程的函数
def initializer_worker():
    # 获取此线程的唯一名称
    name = current_thread().name
    # 将唯一的worker名存储在一个线程局部变量中  
    print(f'Initializing worker thread {name}')
 

def task(identifier):
    sleep(random())
    return identifier
 
with ThreadPoolExecutor(max_workers=2, initializer=initializer_worker) as executor:
    for result in executor.map(task, range(10)):
        print(result)
```

运行这个示例，我们可以看到在运行任何任务之前初始化了两个线程，然后所有10个任务都成功完成了

```
Initializing worker thread ThreadPoolExecutor-0_0
Initializing worker thread ThreadPoolExecutor-0_1
0
1
...
8
9
```



#### 如何详细使用Future Objects

当调用submit()将任务发送到`ThreadPoolExecutor`中异步执行时，将创建Future对象。Future对象提供了检查任务状态(例如，它正在运行吗?)和控制任务执行(例如，取消)的功能。

我们将查看一些检查和操作线程池创建的Future对象的示例

- 如何查看Futures状态
- 如何从Futures中获得结果
- 如何取消Futures
- 如何添加Futures回调

**Future对象的生命周期**

当我们为ThreadPoolExecutor上的任务调用submit()时，会创建一个Future对象。当任务正在执行时，Future对象的状态为“running”。当任务完成时，它的状态为“done”，如果目标函数返回一个值，则可以检索该值

在一个任务运行之前，它会被插入到一个任务队列中，让工作线程接受并开始运行。在这种“预运行”状态下，任务可以被取消，并且处于“已取消”状态。状态为“running”的任务不能取消。

一个`cancelled`的任务也总是处于“完成”状态。
当任务运行时，它会引发未捕获的异常，导致任务停止执行。该异常将被存储并可直接检索，或者在试图检索结果时将重新引发该异常

下图总结了Future对象的生命周期

![](D:\u\网站文档\img\微信截图_20220425153730.png)

**如何查看Future状态**

我们可能需要检查Future对象的两种正常状态:运行状态和已完成状态

每个函数都有自己的函数，当Future对象处于该状态时返回True，否则返回False;例如

- running():如果任务正在运行，则返回True。
- done():如果任务已经完成或被取消，则返回True

我们可以开发简单的示例来演示如何检查Future对象的状态。在这个例子中，我们可以启动一个任务，然后检查它是否正在运行而没有完成，等待它完成，然后检查它是否已经完成而没有运行

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 
def work():
    sleep(0.5)
 
with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    # 确认任务正在运行
    running = future.running()
    done = future.done()
    print(f'Future running={running}, done={done}')
    # 等待任务完成
    wait([future])
    running = future.running()
    done = future.done()
    print(f'Future running={running}, done={done}')
```

运行这个示例，我们可以看到，在任务提交之后，它立即被标记为正在运行，并且在任务完成之后，我们可以确认它已经完成

```
Future running=True, done=False
Future running=False, done=True
```

**如何从Future中获得结果**

当一个任务完成时，我们可以通过调用Future上的result()函数来获取任务的结果。这将返回所执行任务的返回函数的结果，如果函数没有返回值，则返回None

该函数将阻塞，直到任务完成并检索到结果。如果任务已经完成，它将立即返回结果

下面的示例演示了如何从Future对象检索结果。

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
 
def work():
    sleep(1)
    return "all done"
 
with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    # 从任务中获取结果，等待任务完成 
    result = future.result()
    print(f'Got Result: {result}')
```

运行示例提交任务，然后尝试检索结果，阻塞直到结果可用，然后报告接收到的结果

```
Got Result: all done
```

我们还可以设置一个超时，表示我们希望等待结果的时间(以秒为单位)。
如果在得到结果之前超时，则引发TimeoutError。下面的示例演示了超时，展示了如何在任务完成之前放弃等待。

```
from concurrent.futures import TimeoutError
...
with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    try:
        result = future.result(timeout=0.5)
        print(f'Got Result: {result}')
    except TimeoutError:
        print('Gave up waiting for a result')
```

运行该示例表明，我们在半秒后放弃了等待结果(超时)

```
Gave up waiting for a result
```

**如何取消Future**

回想一下，当我们使用submit()或map()将任务放入池中时，任务会被添加到一个内部工作队列中，工作线程可以从队列中删除任务并执行它们。

当一个任务在队列中并且在它被启动之前，我们可以通过调用与该任务关联的Future对象的cancel()来取消它。如果任务被取消，cancel()函数将返回True，否则返回False

让我们通过一个工作示例来演示这一点。我们可以用一个线程创建一个线程池，然后启动一个长时间运行的任务，然后提交第二个任务，请求取消它，然后确认它确实被取消了

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 
def work(sleep_time):
    sleep(sleep_time)
 
with ThreadPoolExecutor(1) as executor:
    future1 = executor.submit(work, 2)
    running = future1.running()
    print(f'First task running={running}')

    future2 = executor.submit(work, 0.1)
    running = future2.running()
    print(f'Second task running={running}')
    # 取消第二个任务
    was_cancelled = future2.cancel()
    print(f'Second task was cancelled: {was_cancelled}')
    # 等待第二个任务完成，以防万一 
    wait([future2])
    # confirm it was cancelled
    running = future2.running()
    cancelled = future2.cancelled()
    done = future2.done()
    print(f'Second task running={running}, cancelled={cancelled}, done={done}')
    # 等待长时间运行的任务完成
    wait([future1])
```

运行这个示例，我们可以看到第一个任务已经启动并正常运行。第二个任务已被调度，但尚未运行，因为线程池已被第一个任务占用。然后我们取消第二个任务，并确认它确实没有运行;它被取消了，现在完成了

```
First task running=True
Second task running=False
Second task was cancelled: True
Second task running=False, cancelled=True, done=True
```

**取消运行中的Future**

现在，让我们尝试取消一个已经完成运行的任务。

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 
def work(sleep_time):
    sleep(sleep_time)
 
with ThreadPoolExecutor(1) as executor:
    future = executor.submit(work, 2)
    running = future.running()
    print(f'Task running={running}')
    # 尝试取消任务
    was_cancelled = future.cancel()
    print(f'Task was cancelled: {was_cancelled}')
    # 等待任务完成
    wait([future])
    running = future.running()
    cancelled = future.cancelled()
    done = future.done()
    print(f'Task running={running}, cancelled={cancelled}, done={done}')
```

运行这个示例，我们可以看到任务按正常方式启动。
然后，我们尝试取消该任务，但如我们所料，这并不成功，因为该任务已经在运行。

然后，我们等待任务完成，然后检查其状态。我们可以看到，任务不再运行，没有像我们预期的那样被取消，而是被标记为未取消。而任务成功地完成了。

```
Task running=True
Task was cancelled: False
Task running=False, cancelled=False, done=True
```

**取消已完成的Future**

考虑一下如果我们试图取消一个已经完成的任务会发生什么。
我们可能认为取消一个已经完成的任务不会有任何影响，而事实正是如此。

```
...
with ThreadPoolExecutor(1) as executor:
    future = executor.submit(work, 2)
    running = future.running()
    wait([future])
    running = future.running()
    cancelled = future.cancelled()
    done = future.done()
    print(f'Task running={running}, cancelled={cancelled}, done={done}')
    was_cancelled = future.cancel()
    print(f'Task was cancelled: {was_cancelled}')
    running = future.running()
    cancelled = future.cancelled()
    done = future.done()
    print(f'Task running={running}, cancelled={cancelled}, done={done}')
```

任务取消失败，执行取消操作后检查状态，确认该任务不受影响

```
Task running=False, cancelled=False, done=True
Task was cancelled: False
Task running=False, cancelled=False, done=True
```

**如何添加Future回调**

我们已经在上面看到了如何添加一个回调到Future。尽管如此，我们还是来看一些完整的例子，包括一些边缘情况。
通过调用add_done_callback()函数并指定要调用的函数名，可以在Future对象上注册一个或多个回调函数

回调函数将在任务完成后立即以Future对象作为参数调用。如果注册了多个回调函数，那么它们将按照注册的顺序被调用，每个回调函数中的任何异常都将被捕获、记录和忽略。这个回调函数将由执行该任务的工作线程调用。
下面的例子演示了如何向Future对象添加回调函数。

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 
# 任务完成时调用的回调函数 
def custom_callback(future):
    print('Custom callback was called')
 
def work():
    sleep(1)
    print('Task is done')
 
with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    # 添加自定义回调
    future.add_done_callback(custom_callback)
    wait([future])
```

运行这个示例，我们可以看到任务首先完成，然后按预期执行回调

```
Task is done
Custom callback was called
```

**使用Future回调时的常见错误**

一个常见的错误是忘记将Future对象作为参数添加到自定义回调中

```
# 任务完成时调用的回调函数  
def custom_callback():
    print('Custom callback was called')
```

如果你注册这个函数并尝试运行代码，你会得到一个TypeError，如下所示

```
Task is done
exception calling callback for <Future at 0x104482b20 state=finished returned NoneType>
...
TypeError: custom_callback() takes 0 positional arguments but 1 was given
```

TypeError中的消息清楚地说明了如何修复这个问题:为Future对象向函数添加单个参数，即使你不打算在回调中使用它

**取消一个Future时执行回调**

我们还可以看到对Future对象的回调对被取消的任务的影响。  这个效果似乎没有在API中记录，但是我们可以期望回调总是被执行，无论任务是正常运行还是被取消。情况就是这样。

下面的示例演示了这一点。
首先，使用单个线程创建线程池。发出占用整个池的长时间运行的任务，然后我们发送第二个任务，向第二个任务添加一个回调，取消它，并等待所有任务完成。

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 
def custom_callback(future):
    print('Custom callback was called')
 
def work(sleep_time):
    sleep(sleep_time)
 
with ThreadPoolExecutor(1) as executor:
    future1 = executor.submit(work, 2)
    running = future1.running()
    print(f'First task running={running}')
    future2 = executor.submit(work, 0.1)
    running = future2.running()
    print(f'Second task running={running}')
    # 添加自定义回调
    future2.add_done_callback(custom_callback)
    # 取消第二个任务
    was_cancelled = future2.cancel()
    print(f'Second task was cancelled: {was_cancelled}')
    # 显式地等待所有任务完成
    wait([future1, future2])
```

运行这个示例，我们可以看到第一个任务已按预期启动。
第二个任务已被调度，但在我们取消它之前没有机会运行它。回调在我们取消任务后立即运行，然后我们在主线程中报告任务确实被正确地取消了

```
First task running=True
Second task running=False
Custom callback was called
Second task was cancelled: True
```

**如何从Future中获取异常**

任务在执行过程中可能引发异常。
如果可以预见到异常，则可以将任务函数的部分封装在try-except块中，并在任务中处理异常。如果任务中发生意外异常，任务将停止执行

我们不能根据任务状态知道是否引发了异常，但是我们可以直接检查异常。然后可以通过exception()函数访问异常。另外，在试图获取结果时调用result()函数也会重新引发异常。

我们可以用一个例子来说明这一点。下面的示例将在任务中引发ValueError，该任务不会被捕获，而是会被线程池捕获，以便我们稍后访问

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 
def work():
    sleep(1)
    raise Exception('This is Fake!')
    return "never gets here"
 
with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    wait([future])
    # 任务执行完成后，查看任务状态  
    running = future.running()
    cancelled = future.cancelled()
    done = future.done()
    print(f'Task running={running}, cancelled={cancelled}, done={done}')
    # 获取的异常
    exception = future.exception()
    print(f'Exception={exception}')
    try:
        result = future.result()
    except Exception:
        print('Unable to get the result')
```

运行该示例将正常启动任务，该任务将休眠一秒钟。
然后，该任务引发一个异常，该异常被线程池捕获。线程池存储异常，任务完成

我们可以看到，在任务完成后，它被标记为未运行、未取消和已完成。然后从任务中访问异常，它与我们有意抛出的异常相匹配。试图通过result()函数访问结果失败，我们捕捉到任务中引发的相同异常

```
Task running=False, cancelled=False, done=True
Exception=This is Fake!
Unable to get the result
```

**如果任务引发异常，回调函数仍然被调用**

我们可能想知道，如果用Future注册回调函数，当任务引发异常时，它是否仍然会执行。
正如我们所料，即使任务引发异常，也会执行回调。我们可以通过更新前面的示例来进行测试，以便在任务失败并出现异常之前注册一个回调函数。

```
...
def custom_callback(future):
    print('Custom callback was called')

with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    future.add_done_callback(custom_callback)
    wait([future])
    running = future.running()
    cancelled = future.cancelled()
    done = future.done()
    print(f'Task running={running}, cancelled={cancelled}, done={done}')
    exception = future.exception()
    print(f'Exception={exception}')
    try:
        result = future.result()
    except Exception:
        print('Unable to get the result')
```

运行示例将像前面一样启动任务，但这一次注册了一个回调函数。
当任务失败并出现异常时，将立即调用回调函数。主线程然后报告失败任务的状态和异常的详细信息。

```
Custom callback was called
Task running=False, cancelled=False, done=True
Exception=This is Fake!
Unable to get the result
```

#### 何时使用ThreadPoolExecutor

ThreadPoolExecutor功能强大且灵活，尽管它并不适合于需要运行后台任务的所有情况。
在本节中，我们将研究一些适合或不适合ThreadPoolExecutor的一般情况，然后我们将研究广泛的任务类，以及它们适合或不适合ThreadPoolExecutor的原因。

**什么时候用ThreadPoolExecutor**

- 您的任务可以由一个没有状态或副作用的纯函数定义
- 您的任务可以包含在一个Python函数中，这可能使它变得简单和容易理解
- 你需要多次执行相同的任务，例如同质任务。
- 您需要对for循环中的集合中的每个对象应用相同的函数

当对一组不同的数据(例如，同构任务、异构数据)应用相同的纯函数时，线程池的工作效果最好。这使得代码更容易阅读和调试。这不是一条规则，只是一个温和的建议

**什么时候用多个ThreadPoolExecutor**

- 你需要执行不同类型的任务;每个任务类型可以使用一个线程池
- 你需要执行一系列的任务或操作;每个步骤可以使用一个线程池

线程池可以操作不同类型的任务(例如异构任务)，尽管如果每个任务类型都有一个单独的线程池，这可能会使程序的组织和调试变得容易。这不是一条规则，只是一个温和的建议

**什么时候不要使用ThreadPoolExecutor**

- 你有一个任务;考虑使用带有target参数的Thread类
- 你有长期运行的任务，例如监视或调度;考虑扩展Thread类
- 你的任务函数需要状态;考虑扩展Thread类。
- 你的任务需要协调;考虑使用Thread和Barrier或Semaphore等模式
- 你的任务需要同步;考虑使用线程和锁。
- 你需要一个事件的线程触发器;考虑使用Thread类。

线程池的最佳点是在调度许多类似的任务时，其结果可以在程序的后面使用。不能完全适合此摘要的任务可能不适合用于线程池。这不是一条规则，只是一个温和的建议

**对io绑定任务使用线程**

对于io绑定的任务，应该使用线程。
io绑定任务是一种涉及对设备、文件或套接字连接进行读写的任务。操作包括IO (input and output)，这些操作的速度与设备、硬盘或网络连接有关。这就是这些任务被称为io约束的原因

cpu非常快。现代的CPU，比如4GHz，每秒可以执行40亿条指令，而且系统中可能有多个CPU。与cpu的速度相比，IO非常慢。
与设备交互、读写文件和套接字连接涉及调用操作系统(内核)中的指令，它将等待操作完成。如果这个操作是你的CPU的主要关注点，比如在你的Python程序的主线程中执行，那么你的CPU将等待许多毫秒甚至许多秒不做任何事情。这可能导致数十亿操作无法执行。我们可以通过在另一个执行线程上执行io绑定操作来释放CPU。这允许CPU启动进程，并将其传递给操作系统(内核)进行等待，然后释放它，让它在另一个应用程序线程中执行

背后还有更多，但这是要点。
因此，我们使用ThreadPoolExecutor执行的任务应该是包含IO操作的任务。例子包括

- 从硬盘读取或写入文件。
- 读或写标准输出，输入或错误(stdin, stdout, stderr)。
- 打印一个文档。
- 下载或上传文件。
- 查询服务器。
- 查询数据库。
- 拍照或录像。
- 还有更多。

如果您的任务不是io绑定的，那么可能不适合使用线程和线程池

**不要在cpu绑定的任务中使用线程**

您可能不应该将线程用于cpu绑定的任务。cpu绑定任务是一种只涉及计算而不涉及IO的任务。这些操作只涉及主存(RAM)或缓存(CPU缓存)中的数据，并对这些数据进行计算。因此，对这些操作的限制是CPU的速度。这就是为什么我们称它们为cpu绑定任务

例子包括

- 计算分形中的点
- 估算Pi
- 素数因子分解
- 解析HTML, JSON等文档。
- 文本处理
- 模型运算

CPU非常快，我们经常有多个CPU。我们想要完成我们的任务，并充分利用现代硬件中的多个CPU核。在Python中通过ThreadPoolExecutor类使用线程和线程池可能不是实现这一目标的途径。
这是因为Python解释器实现方式背后的技术原因。该实现防止了解释器内同时执行两个Python操作，它使用一个主锁来实现这一点，每次只有一个线程可以持有。这被称为全局解释器锁（GIL）

GIL并不邪恶，也不令人沮丧;这是我们在设计应用程序时必须注意和考虑的python解释器的设计决策。

我说过，您“可能”不应该将线程用于cpu绑定的任务。您可以并且可以自由地这样做，但是由于GIL，您的代码将不能从并发性中受益。它的性能可能会更差，因为使用线程会带来上下文切换(CPU从一个执行线程跳转到另一个执行线程)的额外开销。

如果您使用不同的Python解释器实现(例如PyPy、IronPython、Jython等)，那么您可能不受GIL的约束，可以直接为CPU绑定的任务使用线程。

Python提供了一个用于多核任务执行的 [multiprocessing module](https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing)，以及一个ThreadPoolExecutor的同级模块，该模块使用名为ProcessPoolExecutor的进程，可用于cpu绑定任务的并发性

#### ThreadPoolExecutor异常处理

使用线程时，异常处理是一个重要的考虑事项。当意外发生时，代码将引发一个异常，应用程序应该显式地处理该异常，即使这意味着记录它并继续前进

Python线程非常适合与io绑定的任务一起使用，这些任务中的操作通常会引发异常，比如无法访问服务器、网络故障、无法找到文件等等。在使用ThreadPoolExecutor时，有三点可能需要考虑异常处理;它们是:

- 线程初始化期间的异常处理
- 任务执行中的异常处理
- 任务完成时异常处理回调

**线程初始化期间的异常处理**

您可以在配置ThreadPoolExecutor时指定一个自定义初始化函数，线程池启动的每个线程都将在启动线程之前调用初始化函数。

如果初始化函数引发异常，它将破坏线程池。线程池执行的所有当前任务和任何未来的任务将不会运行，并将引发BrokenThreadPool异常。

我们可以通过一个引发异常的人为初始化函数的例子来说明这一点

```
from time import sleep
from random import random
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor
 
def initializer_worker():
    # raise an exception
    raise Exception('Something bad happened!')

def task(identifier):
    sleep(random())
    return identifier
 
# create a thread pool
with ThreadPoolExecutor(max_workers=2, initializer=initializer_worker) as executor:
    for result in executor.map(task, range(10)):
        print(result)
```

如我们所料，运行该示例会失败并出现异常。
线程池按正常方式创建，但一旦我们尝试执行任务，就会创建新的工作线程，并调用自定义工作线程初始化函数，并引发异常。多个线程试图启动，而多个线程依次失败并抛出异常。最后，线程池本身记录了一条消息，说明池已损坏，不能再使用了

这突出表明，如果使用自定义初始化器函数，则必须仔细考虑可能引发的异常并可能处理它们，否则依赖于线程池的所有任务都将面临风险。

**任务执行中的异常处理**

执行任务时可能发生异常。
这将导致任务停止执行，但不会中断线程池。相反，异常将被线程池捕获，并通过exception()函数与任务关联的Future对象可用

另外，如果在Future中调用result()以获得结果，则会重新引发异常。再将任务添加到线程池时，这会影响对submit()和map()的调用

这意味着您有两个选项来处理任务中的异常;他们是

- 处理任务函数中的异常
- 从任务中获取结果时处理异常

**处理任务内部的异常**

在任务中处理异常意味着需要某种机制让结果的接收者知道发生了意外，这可以通过函数的返回值来实现，例如None。或者，您可以重新引发一个异常，并让接收者直接处理它。第三种选择可能是使用一些更广泛的状态或全局状态，可以通过引用传递给函数调用。

下面的示例定义了将引发异常的工作任务，但将捕获异常并返回指示失败情况的结果

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor

def work():
    sleep(1)
    try:
        raise Exception('Something bad happened!')
    except Exception:
        return 'Unable to get the result'
    return "never gets here"
 
with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    result = future.result()
    print(result)
```

运行该示例将按正常方式启动线程池，发出任务，然后阻塞等待结果。
该任务引发异常，接收到的结果是一条错误消息。这种方法对于接收方代码来说是相当干净的，并且适合于由submit()和map()发出的任务。对于失败的情况，可能需要对自定义返回值进行特殊处理

```
Unable to get the result
```

**处理任务结果的接收者的异常**

在任务中处理异常的另一种方法是将责任留给结果的接收者

这可能感觉是一个更自然的解决方案，因为它匹配相同操作的同步版本，例如，如果我们在for循环中执行函数调用。

这意味着接收方必须知道任务可能引发的错误类型，并显式地处理它们。下面的示例定义了一个引发Exception的简单任务，然后由接收者在试图从函数调用获得结果时处理该任务。

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
 
def work():
    sleep(1)
    raise Exception('Something bad happened!')
    return "never gets here"
 
with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    try:
        result = future.result()
    except Exception:
        print('Unable to get the result')
```

运行该示例将创建线程池并按正常方式提交工作。任务失败并出现错误，线程池捕获异常并存储它，然后在将来调用result()函数时重新引发它。结果的接收者接受异常并捕获它，报告一个失败案例。

```
Unable to get the result
```

还可以通过调用Future对象上的exception()函数直接检查异常。这个函数会阻塞，直到出现异常并超时，就像调用result()一样

如果异常从未发生，任务被取消或成功完成，则exception()将返回None值。

在下面的示例中，我们可以演示任务中异常情况的显式检查

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
 
def work():
    sleep(1)
    raise Exception('Something bad happened!')
    return "never gets here"
 
with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    exception = future.exception()
    if exception:
         print(exception)
    else:
        result = future.result()
        print(result)
```

运行示例将创建并提交每个正常工作。
接收方检查异常情况，它将阻塞，直到引发异常或任务完成。接收到异常并通过报告它来处理

```
Something bad happened!
```

我们不能为每个任务检查Future对象的exception()函数，因为map()不提供对Future对象的访问。

更糟糕的是，在使用map()提交任务时，不能使用处理接收方异常的方法，除非您包装整个迭代。
我们可以通过使用map()提交一个碰巧引发Exception的任务来演示这一点。

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
 
def work(value):
    sleep(1)
    raise Exception('Something bad happened!')
    return f'Never gets here {value}'
 
with ThreadPoolExecutor() as executor:
    for result in executor.map(work, [1]):
        print(result)
```

运行该示例提交单个任务(map()的糟糕用法)并等待第一个结果。
任务引发异常，主线程退出，如我们所料

```
Traceback (most recent call last):
...
    raise Exception('Something bad happened!')
Exception: Something bad happened!
```

这突出表明，如果使用map()将任务提交到线程池，那么任务应该处理自己的异常，或者足够简单，不会出现异常

**回调中的异常处理**

当使用ThreadPoolExecutor时，我们必须考虑的最后一种异常处理情况是在回调函数中。这些回调函数总是被调用，即使任务被取消或本身发生异常而失败

回调函数可能会出现异常而失败，并且它不会影响已经注册的其他回调函数或任务。异常由线程池捕获，作为异常类型消息记录，然后继续过程。从某种意义上说，回调可以悄无声息地失败。

我们可以通过一个具有多个回调函数的工作示例来演示这一点，其中第一个回调函数将引发异常

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 
def custom_callback1(future):
    raise Exception('Something bad happened!')
    print('Callback 1 called.')
 
def custom_callback2(future):
    print('Callback 2 called.')
 
def work():
    sleep(1)
    return 'Task is done'
 
with ThreadPoolExecutor() as executor:
    future = executor.submit(work)
    future.add_done_callback(custom_callback1)
    future.add_done_callback(custom_callback2)
    result = future.result()
    sleep(0.1)
    print(result)
```

当任务完成时，调用第一个回调，该回调会失败并出现异常。异常被记录并报告在控制台上(日志记录的默认行为)

线程池没有中断并继续运行。第二个回调被成功调用，最后，主线程获得任务的结果。

```
exception calling callback for <Future at 0x101d76730 state=finished returned str>
Traceback (most recent call last):
...
    raise Exception('Something bad happened!')
Exception: Something bad happened!
Callback 2 called.
Task is done
```

这强调了，如果回调函数预期会引发异常，如果您希望失败影响任务本身，则必须显式地处理并检查它。

#### ThreadPoolExecutor内部是如何工作的

类的内部工作影响我们使用线程池的方式和预期的行为，特别是取消任务。如果不了解这一点，线程池的一些行为从外部来看可能会令人困惑

你可以在这里看到ThreadPoolExecutor和基类的源代码:

- [cpython/Lib/concurrent/futures/thread.py](https://github.com/python/cpython/blob/3.10/Lib/concurrent/futures/thread.py)
- [cpython/Lib/concurrent/futures/_base.py](https://github.com/python/cpython/blob/3.10/Lib/concurrent/futures/_base.py)

**任务被添加到内部队列**

通过将任务添加到内部队列，任务被发送到线程池。
回想一下，队列是一种数据结构，在缺省情况下，项目被添加到一端，并以先进先出(FIFO)的方式从另一端检索。

该队列是一个SimpleQueue对象，它是一个线程安全的queue实现。这意味着我们可以从任何线程向池中添加工作，并且工作队列不会因为并发的put()和get()操作而损坏。

任务队列的使用说明了已经添加或计划但尚未运行的任务和可以取消的任务之间的区别

回想一下，线程池有固定数量的工作线程。队列上的任务数可能超过当前线程数或当前可用线程数。在这种情况下，任务可能会在一段时间内处于计划状态，从而允许在关闭池时直接或批量取消它们

任务被包装在一个名为`_WorkItem`的内部对象中。这将捕获诸如要调用的函数、参数、关联的Future对象以及在任务执行期间发生异常时的处理等细节。这解释了任务中的异常如何不会关闭整个线程池，但可以在任务完成后进行检查和访问

当工作线程从队列中检索到`_WorkItem`对象时，它将检查任务在执行前是否被取消。如果是，它将立即返回，而不执行任务的内容

这在内部解释了线程池如何实现取消，以及为什么不能取消正在运行的任务。

**根据需要创建工作线程**

创建线程池时不会创建工作线程。相反，工作线程是按需或即时创建的。每次将任务添加到内部队列时，线程池将检查活动线程的数量是否小于线程池支持的线程上限。如果是，则创建一个额外的线程来处理新工作。

一旦一个线程完成了一个任务，它将在队列中等待新工作的到来。当新工作到达时，等待队列中的所有线程都将得到通知，其中一个线程将消耗该工作单元并开始执行它

这两点说明了池如何在达到限制之前只创建新线程，以及如何重用线程，等待新任务而不消耗计算资源。它还显示线程池在完成固定数量的工作单元后不会释放线程。也许这在将来会成为API的一个很好的补充。

#### ThreadPoolExecutor最佳实践

既然我们已经知道了ThreadPoolExecutor的工作方式以及如何使用它，让我们回顾一下在将线程池引入Python程序时需要考虑的一些最佳实践。

为了保持简单，这里有五个最佳实践;它们是:

- 使用上下文管理器
- 在异步for循环中使用map()
- 使用submit()和as_completed()
- 使用独立的功能作为任务
- 用于io绑定任务(可能)

**使用上下文管理器**

使用线程池时使用上下文管理器，并处理分配到线程池的所有任务和管理器内的处理结果。

```
with ThreadPoolExecutor(10) as executor:
	# ...
```

记得在上下文管理器中创建线程池时配置它，特别是通过设置池中使用的线程数

使用上下文管理器可以避免出现这样的情况:您已经显式实例化了线程池，却忘记通过调用shutdown()手动关闭它

**在异步for循环中使用map()**

如果您有一个for循环，它将一个函数应用于列表中的每一项，那么可以使用map()函数异步地分派任务

```
for item in mylist:
	result = myfunc(item)
	# do something...
	
for result in map(myfinc, mylist):
	# do something...
```

使用线程池上的map()函数可以使这两种情况都变成异步的

```
for result in executor.map(myfunc, mylist):
	# do something...
```

如果您的目标任务函数有副作用，请不要使用map()函数。

如果您的目标任务函数没有参数或有多个参数，请不要使用map()函数

如果需要控制每个任务的异常处理，或者希望按任务完成的顺序获得任务的结果，则不要使用map()函数

**使用submit()和as_completed()**

如果您希望按照任务完成的顺序处理结果，而不是按照任务提交的顺序，那么可以使用submit()和as_completed()

```
futures = [executor.submit(myfunc, item) for item in mylist]
# 按任务完成的顺序处理来自任务的结果  
for future in as_completed(futures):
	result = future.result()
	# do something...
```

如果需要按照任务提交到线程池的顺序处理结果，则不要使用submit()和as_completed()组合。

如果你需要所有任务的结果来继续，不要使用submit()和as_completed()组合;使用wait()模块函数可能会更好。

不要在简单的异步for循环中使用submit()和as_completed()组合;使用map()可能会更好

**使用独立的函数作为任务**

如果您的任务是独立的，则使用ThreadPoolExecutor。
这意味着每个任务不依赖于可以同时执行的其他任务。它也可能意味着任务不依赖于任何数据，除了通过函数参数提供给任务的数据

ThreadPoolExecutor非常适合那些不改变任何数据的任务，比如没有副作用的任务，即所谓的纯函数。

线程池可以组织成数据流和管道，以实现任务之间的线性依赖性，每个任务类型可能有一个线程池。

线程池不是为需要协调的任务设计的;你应该考虑使用Thread类和像Barrier和Semaphore这样的协调模式。

线程池不是为需要同步的任务设计的;你应该考虑使用Thread类和锁模式，比如Lock和RLock。

**用于io绑定任务(可能)**

只对io绑定的任务使用ThreadPoolExecutor。这些任务可能涉及到与外部设备的交互，如外设(如相机或打印机)、存储设备(如存储设备或硬盘驱动器)或另一台计算机(如套接字通信)。

线程和线程池(如ThreadPoolExecutor)可能不适合cpu绑定的任务，比如对内存中的数据进行计算。

这是因为Python解释器中的设计决策使用了称为全局解释器锁(GIL)的主锁，从而防止多个Python指令同时执行

这个设计决策是在Python解释器的参考实现中做出的(来自Python.org)，但可能不会影响其他解释器(如PyPy、Iron Python和Jython)



[官网](https://docs.python.org/3/library/concurrent.futures)

[原文链接](https://superfastpython.com/threadpoolexecutor-in-python/)

