#### 使用ThreadPoolExecutor时常见的错误



**1. 如何停止正在运行的任务?**

ThreadPoolExecutor中的任务可以在它开始运行之前取消。
在本例中，必须通过调用submit()将任务发送到池中，它返回一个Future对象。然后您可以在以后调用cancel()函数。如果任务已经在运行，则线程池无法取消、停止或终止它。相反，您必须将此功能添加到任务中

种方法可能是使用线程安全标志，比如**threading.Event**，如果设置，将指示所有任务必须尽快停止运行。然后，您可以更新您的目标任务函数或函数，以经常检查此标志的状态

这可能需要您更改任务的结构。例如，如果您的任务从文件或套接字读取数据，您可能需要将读取操作更改为在循环中的数据块中执行，以便在每次循环迭代时都可以检查标志的状态

下面的示例提供了一个模板，可用于向目标任务函数添加事件标志，以检查停止条件，以关闭所有当前运行的任务。

```
from time import sleep
from threading import Event
from concurrent.futures import ThreadPoolExecutor
 
# 模拟目标任务函数
def work(event):
    # 假装长时间读取数据
    for _ in range(100):
        # 假装读取一些数据
        sleep(1)
        # 检查标志的状态
        if event.is_set():
            # 现在停止这个任务
            print("没有做完，要求停止")
            return
    return "All done!"
 
# 创建事件以关闭所有正在运行的任务  
event = Event()


executor = ThreadPoolExecutor(5)
# 该事件可以作为参数传递给每个目标任务函数
futures = [executor.submit(work, event) for _ in range(50)]
# 暂停2s
print('任务正在运行...')
sleep(2)
# 取消所有调度任务
print('取消所有调度任务...')
for future in futures:
    future.cancel()
# 停止所有当前运行的任务
print('停止所有当前运行的任务...')
event.set()  # 通过事件停止正在运行的任务
# 关闭线程池，等待所有任务完成
print('Shutting down...')
executor.shutdown()
```

运行这个示例首先创建一个线程池，其中有5个工作线程，并调度50个任务。创建一个事件对象并将其传递给每个任务，在每个迭代中检查它是否被设置，如果设置，则退出任务。前5个任务开始执行几秒钟，然后我们决定关闭一切。

首先，我们取消所有还没有运行的计划任务，这样，如果它们从队列进入工作线程，它们就不会开始运行。然后我们标记设置事件以触发所有正在运行的任务停止。然后关闭线程池，等待所有正在运行的线程完成它们的执行。

这五个正在运行的线程在下一个循环迭代中检查事件的状态并退出，打印一条消息

```
任务正在运行...
取消所有调度任务...
停止所有当前运行的任务...
Shutting down...
没有做完，要求停止
没有做完，要求停止
没有做完，要求停止
没有做完，要求停止
没有做完，要求停止
```

**如何等待所有任务完成?**

有几种方法可以等待ThreadPoolExecutor中的所有任务完成。

首先，如果由于调用了submit()，所以线程池中的所有任务都有一个Future对象，那么可以将任务集合提供给wait()模块函数。默认情况下，当所有提供的Future对象完成后，该函数将返回

```
wait(futures)  # 等待所有任务完成
```

或者，也可以枚举Future对象列表，并尝试从每个对象获取结果。此迭代将在所有结果可用时完成，这意味着所有任务都已完成

```
# 通过获取所有结果来等待所有任务完成  
for future in futures:
	result = future.result()
# 所有任务完成
```

另一种方法是关闭线程池。我们可以将`cancel_futures`设置为True，这将取消所有计划的任务，并等待所有当前运行的任务完成

```
# 关闭池，取消计划任务，当正在运行的任务完成时返回  
executor.shutdown(wait=True, cancel_futures=True)
```

您还可以关闭池，而不取消计划任务，但仍然等待所有任务完成。这将确保所有正在运行和计划的任务在函数返回之前完成。这是shutdown()函数的默认行为，但是显式地指定是一个好主意

```
# 关闭池，在所有计划的和正在运行的任务完成后返回
executor.shutdown(wait=True, cancel_futures=False)
```

**如何动态地改变线程的数量?**

您不能动态地增加或减少ThreadPoolExecutor中的线程数。当ThreadPoolExecutor在对象构造函数的调用中配置时，线程的数量是固定的。例如

```
executor = ThreadPoolExecutor(20)
```

**如何从任务中进行日志记录**

您的目标任务函数是由线程池中的工作线程执行的，您可能会关心从这些任务函数中进行日志记录是否线程安全。

也就是说，如果两个线程同时尝试，日志是否会损坏。答案是否定的，日志不会被破坏。默认情况下，Python日志功能是线程安全的。

例如，请参阅日志模块API文档中的以下引用:

> 日志模块是线程安全的，不需要它的客户端做任何特殊的工作。它通过使用线程锁来实现这一点;有一个锁用于序列化对模块共享数据的访问，每个处理程序也创建一个锁用于序列化对其底层I/O的访问

因此，您可以直接从目标任务函数中进行日志记录。

**如何划分任务和线程池?**

您可以直接对目标任务函数进行单元测试，也许可以模拟所需的任何外部资源。您可以使用不与外部资源交互的模拟任务对线程池的使用进行单元测试

单元测试的任务和线程池本身必须考虑作为设计的一部分,可能需要连接到IO资源是可配置的,这样它就可以被假设,和目标任务函数的线程池是可配置的,这样它就可以被假设了

**如何比较串行和并行性能?**

您可以比较使用和不使用线程池时程序的性能。这是一个很有用的练习，可以确认在程序中使用ThreadPoolExecutor能够提高速度

也许最简单的方法是手动记录代码的开始和结束时间，并从开始时间减去结束时间，以报告总执行时间。然后记录使用和不使用线程池时的时间。

```
import time
 
# 记录开始时间
start_time = time.time()
# 是否使用线程池
# ....
time.sleep(3)
# 记录结束时间
end_time = time.time()
total_time = end_time - start_time
print(f'Execution time: {total_time:.1f} seconds.')
```

使用平均程序执行时间可能比一次性运行提供更稳定的程序时间。您可以在没有线程池的情况下记录程序的执行时间3次或更多次，然后计算平均时间，即时间之和除以总运行次数。然后重复这个练习来计算使用线程池的平均时间

这可能只适用于程序的运行时间为分钟而不是小时的情况。然后，你可以通过计算速度倍数来比较串行和并行版本

- 加速倍数=串行时间/并行时间

例如，如果一个程序的串行运行花费了15分钟(900秒)，而带有ThreadPoolExecutor的并行版本花费了5分钟(300秒)，那么这个百分比的倍数将计算为:

- 加速倍数= 900 / 300 = 3

就是说，带有ThreadPoolExecutor的并行版本的程序要快3倍或3倍。你可以将加速倍数乘以100得到一个百分比

- 加速百分比=加速倍数* 100

在本例中，并行版本比串行版本快300%

**如何在map()中设置chunksize ?**

ThreadPoolExecutor上的map()函数接受一个名为“chunksize”的参数，该参数默认为1。参数chunksize没有被ThreadPoolExecutor使用;它只被ProcessPoolExecutor使用，因此您可以放心地忽略它

在使用ThreadPoolExecutor时，设置此参数不会执行任何操作。

**如何提交后续任务?**

有些任务要求执行第二个任务，第二个任务以某种方式利用第一个任务的结果

我们可以称其为为每个提交的任务执行后续任务的需要，这可能在某种程度上取决于结果。

提交后续任务有几种方法。一种方法是在处理第一个任务的结果时提交后续任务。

例如，我们可以在第一个任务完成时处理它们的结果，然后在需要时为每个后续任务手动调用submit()，并将新的future对象存储在第二个列表中以供以后使用

用一个完整的例子来说明提交后续任务的具体情况

```
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
 
def task1():
    value = random()
    sleep(value)
    print(f'Task 1: {value}')
    return value
 

def task2(value1):
    value2 = random()
    sleep(value2)
    print(f'Task 2: value1={value1}, value2={value2}')
    return value2
 

with ThreadPoolExecutor(5) as executor:
    # 发送第一个任务
    futures1 = [executor.submit(task1) for _ in range(10)]
    # 按照完成的顺序处理结果
    futures2 = list()
    for future1 in as_completed(futures1):
        result = future1.result()
        # 检查我们是否应该触发后续任务
        if result > 0.5:
            future2 = executor.submit(task2, result)
            futures2.append(future2)
```

运行这个示例将启动一个线程池，其中有5个工作线程，并提交10个任务。然后，当任务完成时，我们处理任务的结果。如果第一轮任务的结果需要一个后续任务，我们提交后续任务，并在第二个列表中跟踪Future对象。

这些后续任务将根据需要提交，而不是等待所有第一轮任务完成，这是使用带有Future对象列表的as_completed()函数的一个很好的好处

您可能希望为后续任务使用单独的线程池，以保持事情的独立性，我不建议在任务中提交新任务。这将需要作为全局变量或通过传入访问线程池，并将打破任务是没有副作用的纯函数的想法，这是使用线程池时的一个良好实践

**如何为每个线程存储本地状态?**

您可以在ThreadPoolExecutor中为工作线程使用线程本地变量。

一个常见的模式是为每个工作线程使用一个定制的初始化器函数来设置一个特定于每个工作线程的线程局部变量。
然后，每个任务中的每个线程都可以使用这个线程局部变量，这就要求任务知道线程局部机制。

我们可以通过一个工作示例来演示这一点。
首先，我们可以定义一个自定义初始化器函数，它接受一个线程局部上下文，并为每个工作线程设置一个名为“key”的自定义变量，该变量的值在0.0到1.0之间。

```
# 用于初始化工作线程的函数
def initializer_worker(local):
    # 为工作线程生成一个唯一的值
    local.key = random()
    # 将唯一的工作键存储在一个线程局部变量中  
    print(f'Initializing worker thread {local.key}')
    
```

然后，我们可以定义目标任务函数来获取相同的线程局部上下文，并为工作线程访问线程局部变量并使用它。

```
def task(local):
    mykey = local.key
    sleep(mykey)
    return f'Worker using {mykey}'
```

然后，我们可以配置新的ThreadPoolExecutor实例，以使用带有所需本地参数的初始化器

```
# 获取本地上下文
local = threading.local()
# create a thread pool
executor = ThreadPoolExecutor(max_workers=2, initializer=initializer_worker, initargs=(local,))
```

然后将任务分派到具有相同线程本地上下文的线程池中

```
futures = [executor.submit(task, local) for _ in range(10)]
```

结合这一点，下面列出了使用带有线程本地存储的ThreadPoolExecutor的完整示例

```
from time import sleep
from random import random
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 

def initializer_worker(local):
    local.key = random()
    print(f'Initializing worker thread {local.key}')
 

def task(local):
    mykey = local.key
    sleep(mykey)
    return f'Worker using {mykey}'
 

local = threading.local()

executor = ThreadPoolExecutor(max_workers=2, initializer=initializer_worker, initargs=(local,))

futures = [executor.submit(task, local) for _ in range(10)]

for future in futures:
    result = future.result()
    print(result)
executor.shutdown()
print('done')
```

首先运行示例配置线程池以使用我们的自定义初始化器函数，该函数为每个工作线程设置一个具有惟一值的线程局部变量，在本例中是两个线程，每个线程的值在0到1之间。

**如何显示所有任务的进度?**

有许多方法可以显示ThreadPoolExecutor正在执行的任务的进度

也许最简单的方法是使用一个回调函数来更新进度指示器。这可以通过定义进度指示器函数并通过add_done_callback()函数将其注册到每个任务的Future对象中来实现。

简单的进度指示器是为每个完成的任务在屏幕上打印一个点。下面的示例演示了这个简单的进度指示器。

```
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 
# 简单的进度指示器回调函数
def progress_indicator(future):
    print('.', end='', flush=True)

def task(name):
    sleep(random())
 
with ThreadPoolExecutor(2) as executor:
    futures = [executor.submit(task, i) for i in range(20)]
    # 注册进度指示器回调
    for future in futures:
        future.add_done_callback(progress_indicator)
print('\nDone!')
```

运行这个示例将启动一个具有两个工作线程的线程池，并分发20个任务。向每个Future对象注册一个进度指示器回调函数，该函数在每个任务完成时打印一个点，确保每次调用print()都会刷新标准输出，并且不会打印新行。

这确保了无论打印的线程是什么，我们都能立即看到点，并且所有的点都出现在一行上

```
....................
Done!
```

更详细的进度指示器必须知道任务的总数，并将使用线程安全计数器来更新所有待完成任务中的已完成任务数的状态。

**我们需要检查`__main__`吗**

当使用ThreadPoolExecutor时，你不需要检查`__main__`。当使用名为`ProcessPoolExecutor`的池的Process版本时，你需要检查`__main__`

**如何为添加了map()的任务获得一个Future 对象?**

当您调用map()时，它会为每个任务创建一个Future对象，在内部，对提供给map()调用的可迭代对象中的每一项调用submit()

然而，对于通过map()发送到线程池的任务，没有干净的方法来访问Future对象

ThreadPoolExecutor对象的内部工作队列上的每个任务都是一个_WorkItem的实例，该实例具有该任务的Future对象的引用。您可以访问ThreadPoolExecutor对象的内部队列，但是没有安全的方法来枚举队列中的项目而不删除它们。

如果任务需要一个Future对象，可以调用submit()。

**我可以在上下文管理器中调用shutdown()吗?**

您可以在上下文管理器中调用shutdown()，但是用例并不多。它不会造成我能看到的错误

如果你想取消所有的计划任务，并且你没有访问Future对象的权限，并且你想在等待所有正在运行的任务停止之前进行其他清理，你可能需要显式调用shutdown()。如果你发现自己处于这种情况，那将是很奇怪的。
然而，这里有一个从上下文管理器中调用shutdown()的示例。

```
from time import sleep
from concurrent.futures import ThreadPoolExecutor
 
def task(name):
    sleep(2)
    print(f'Done: {name}')
 
with ThreadPoolExecutor(1) as executor:
    print('Sending in tasks...')
    futures = [executor.submit(task, i) for i in range(10)]
    # 在上下文管理器中显式关闭  
    print('Shutting down...')
    executor.shutdown(wait=False, cancel_futures=True)
    # 当上下文管理器退出时，再次调用Shutdown  
    print('Waiting...')
print('Doing other things...')
```

然后显式地在线程池中调用shutdown并取消所有计划的任务，而无需等待。然后退出上下文管理器，等待所有任务完成。第二次关闭按预期工作，等待一个正在运行的任务完成后返回

```
Sending in tasks...
Shutting down...
Waiting...
Done: 0
Doing other things...
```

#### 使用ThreadPoolExecutor的常见异议

ThreadPoolExecutor可能不是程序中所有多线程问题的最佳解决方案。也就是说，可能还有一些误解妨碍您在程序中充分和最好地利用ThreadPoolExecutor的功能

**全局解释器锁(GIL)**

全局解释器锁(Global Interpreter Lock，简称GIL)是参考Python解释器的一个设计决策。它指的是这样一个事实:Python解释器的实现使用了一个主锁，防止多个Python指令同时执行。

这可以防止Python程序中出现多个执行线程，特别是在每个Python进程中，即Python解释器的每个实例中。

GIL的实现意味着Python线程可能是并发的，但不能并行运行。回想一下，并发意味着可以有多个任务同时进行;并行意味着同时执行多个任务。并行任务是并发的，并发任务可以并行执行，也可以不并行执行

启发式背后的原因,Python线程只能用于IO-bound任务,而不是cpu密集型任务,IO-bound任务会在操作系统内核中等待远程资源响应(不执行Python指令),允许其他Python线程运行Python和执行指令。

换句话说，GIL并不意味着我们不能在Python中使用线程，只是Python线程的一些用例是可行的或合适的

这个设计决策是在Python解释器的参考实现中做出的(来自Python.org)，但可能不会影响允许多个Python指令并行执行的其他解释器(如PyPy、Iron Python和Jython)。

**Python线程是“真正的线程”吗?**

是的，Python使用真正的系统级线程，也称为内核级线程，这是Windows、Linux和MacOS等现代操作系统提供的功能

Python线程不是软件级线程，有时称为用户级线程或绿色线程。

**Python线程不是buggy吗?**

不是，Python线程没有bug。Python线程是Python平台的第一类功能，并且已经存在很长时间了

**对于并发性来说，Python不是一个糟糕的选择吗?**

开发人员喜欢python的原因有很多，最常见的原因是它易于使用和快速开发。Python通常用于粘合代码、一次性脚本，但越来越多地用于大型软件系统

如果你正在使用Python，然后你需要并发，那么你就用你拥有的。这个问题没有意义

如果您需要并发性，而又没有选择一种语言，那么另一种语言可能更合适，也可能不合适。考虑项目的功能性和非功能性需求(或用户需求、希望和期望)的全部范围，以及不同开发平台的功能。

**为什么不总是使用ProcessPoolExecutor ?**

ProcessPoolExecutor支持进程池，而不像ThreadPoolExecutor支持线程池

线程和进程是完全不同的，选择其中一个是有意的。python程序是一个具有主线程的进程。您可以在Python进程中创建许多额外的线程。您还可以派生或生成许多Python进程，每个进程将有一个线程，并可能生成其他线程

更广泛地说，线程是轻量级的，可以共享进程中的内存(数据和变量)，而进程是重量级的，需要更多的开销，并对共享内存(数据和变量)施加更多限制。

通常，进程用于cpu绑定的任务，线程用于io绑定的任务，这是一种很好的启发式方法，但不一定是这样。

也许ProcessPoolExecutor更适合您的特定问题。也许你可以试一试

**为什么不使用threading.Thread呢?**

ThreadPoolExecutor类似于Python线程的“自动模式”。如果您有一个更复杂的用例，您可能需要直接使用**threading.Thread** 类

这可能是因为使用锁定机制的线程之间需要更多的同步，以及/或使用屏障和信号量的线程之间需要更多的协调

您可能有一个更简单的用例，例如单个任务，在这种情况下，线程池可能是一个过于繁重的解决方案。

也就是说，如果您发现自己在纯函数(没有副作用的函数)中使用带有target关键字的Thread类，那么您可能更适合使用ThreadPoolExecutor

**为什么不使用AsyncIO?**

AsyncIO可以替代ThreadPoolExecutor，syncIO被设计成在一个线程中支持大量的IO操作，可能是数千到数万

它需要一种替代的编程范式，称为响应式编程，这对初学者来说是一个挑战。

然而，对于许多应用程序来说，它可能是使用线程池的更好选择。





[官网](https://docs.python.org/3/library/concurrent.futures)

[原文链接](https://superfastpython.com/threadpoolexecutor-in-python/)

