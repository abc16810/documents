### 线程

- 由于全局解释锁（GIL）Python的线程不能对多核CPU并行运行字节码，即Python为了保证线程安全而采取的独立线程运行的限制,说白了就是一个核只能在同一时间运行一个线程.
- 尽管GIL，Python的线程仍然是有用的 因为他们提供了一个简单的方法来在看似同一时间做多件事情。

#### 什么是Python线程

线程，有时被称为轻量级进程(Lightweight Process，LWP），是程序执行流的最小单元。

当我们运行Python脚本时，它会启动一个Python解释器实例，在主线程中运行我们的代码。主线程是Python进程的默认线程。我们可以开发程序并发地执行任务，在这种情况下，我们可能需要创建和运行新的线程。在没有我们的程序的情况下，这些将是执行的并发线程

当我们创建并运行一个新线程时，Python将对底层操作系统进行系统调用，并请求创建一个新线程并开始运行新线程

每个Python程序都是一个进程，其中有一个线程，称为主线程，用于执行程序指令。实际上，每个进程都是执行Python指令(Python字节码)的Python解释器的一个实例，它的级别比你在Python程序中输入的代码略低

- 进程:Python解释器的实例至少有一个名为MainThread的线程。
- 线程:Python进程中的执行线程，如主线程或新线程

**生命周期**

Python线程的生命周期有三个步骤:一个新线程、一个正在运行的线程和一个已终止的线程。
在运行时，线程可能正在执行代码，也可能被阻塞，等待其他线程或外部资源。虽然，不是所有线程都可能阻塞，但根据新线程的特定用例，它是可选的。

- 新线程。
- 运行的线程。
  - 阻塞的线程(可选)。
- 终止线程

一个正在运行的线程可能会以多种方式阻塞，例如从文件或套接字读取或写入，或者等待并发原语(如信号量或锁)。阻塞后，线程将再次运行。最后，线程可能在完成代码执行后终止，也可能引发错误或异常

![](D:\u\网站文档\img\微信截图_20220427085336.png)

我们可能需要在Python进程中创建额外的线程来并发地执行任务。Python通过 [**threading.Thread**](https://docs.python.org/3/library/threading.html)类提供了真正的简单(系统级别)线程

**在线程中运行函数**

通过创建thread类的实例并通过target参数指定要在新线程中运行的函数，任务可以在新线程中运行

```
import threading
import time
 # 一个简单的任务，阻塞1秒并打印一条消息（当前线程）
def show(args):
    time.sleep(1)  # 暂停一下
    print ("thread" +str(args))
 
for i in range(10):
    t = threading.Thread(target=show,args=(i,))  # 创建一个线程来执行show()函数
    t.start() # start()函数将立即返回，但不会立即启动线程，而是允许操作系统安排函数尽快执行
    print('等待线程%s结束...' % i)
    t.join()  # 显式地阻塞并等待线程完成执行
```

我们无法控制线程何时精确执行或哪个CPU核心执行它。这两个都是底层操作系统处理的低级职责

上述代码创建了10个“前台”线程，然后控制器就交给了CPU，CPU根据指定算法进行调度 通过 args 给函数传递参数，也可以使用 kwargs 通过字典传递。

**扩展线程类**

对于threading模块中的Thread类，本质上是执行了它的run方法。因此可以自定义线程类，让它继承Thread类，然后重写run方法

接下来，我们可以创建CustomThread类的实例，并调用start()函数开始在另一个线程中执行run()函数。在内部，start()函数将调用run()函数

```
import threading
class Mythreading(threading.Thread):
 
    def __init__(self, func, args):
    	super(Mythreading, self).__init__()
    	self.func = func
    	self.args = args
 
    def run(self):
    	self.func(self.args)
 
def f1(args):
    print("thread" +str(args))
 
t = Mythreading(f1, 123)
t.start()
t.join()
```

获取值,我们可能需要从线程中检索数据，例如返回值。run()函数无法将值返回给start()函数并返回给调用者。相反，我们可以从run()函数中返回值，方法是将它们存储为实例变量，并让调用者从这些实例变量中检索数据

```
class Mythreading(threading.Thread):

    def run(self):
        sleep(1)
        print('这是来自另一个线程')
        # store return value
        self.value = 99

t = Mythreading()
t.start()
t.join()
# 获取run返回的值
value = t.value
print(f'Got: {value}')
```

#### 线程实例属性

- name 线程名，线程在每个进程中以某种独特的方式自动命名，形式为“Thread-%d”，其中%d是表示进程中的线程号

  ```
  from threading import Thread
  thread = Thread()
  print(thread.name)  # Thread-1
  ```

- daemon 是否守护线程，守护线程是后台线程的名称。默认情况下，线程是非守护进程线程。Python程序只有在所有非守护进程线程退出后才会退出。例如，主线程是非守护线程，这意味着守护线程可以在后台运行，而不必结束

  ```
  print(thread.daemon)  # False
  ```

- Identifier 标识符 在Python进程中，每个线程都有一个唯一的标识符(id)，由Python解释器分配。该标识符是一个只读的正整型值，只有在线程启动后才会被分配, 。通过`ident`属性的可以访问分配给线程的标识符,如果尚未启动，则为None

  ```
  from threading import Thread
  thread = Thread()
  print(thread.ident)  # None
  thread.start()
  print(thread.ident) # 11672
  ```

- native Identifier 本地标识符，每个线程都有一个由操作系统分配的唯一标识符。Python线程是真正的原生线程，这意味着我们创建的每个线程实际上都是由底层操作系统创建和管理(调度)的。因此，操作系统将为系统上(跨进程)创建的每个线程分配一个唯一的整数

  ```
  from threading import Thread
  thread = Thread()
  print(thread.native_id)  # None
  thread.start()
  print(thread.native_id) # 13788
  ```

- alive  线程是否在运行。正在运行指启动后、终止前。这意味着在调用start()方法之前和run()方法完成之后，线程将不是活动的

  ```
  from time import sleep
  from threading import Thread
  thread = Thread(target=lambda:sleep(1))
  print(thread.is_alive())  # False
  thread.start()
  print(thread.is_alive())  #True
  thread.join() 
  print(thread.is_alive()) # False
  ```

#### 配置线程

线程有两个属性可以配置，它们是线程的名称和线程是否是守护进程

- 配置线程名称

  ```
  from threading import Thread
  thread = Thread(name='MyThread')
  print(thread.name)  # MyThread
  # 线程的名称也可以通过“name”属性设置
  thread = Thread()
  thread.name = 'MyThread'
  ```

- 配置守护进程，线程可以配置为守护进程，也可以不配置为守护进程，在并发编程中，大多数线程，包括主线程，默认情况下是非守护线程(不是后台线程)。

  ```
  from threading import Thread
  thread = Thread(daemon=True)
  print(thread.daemon)  # True
  # thread.daemon = True
  ```

#### 主线程

每个Python进程都有一个默认线程，称为“主线程”，当你执行一个Python程序时，它是在主线程中执行的。
主线程是为每个Python进程创建的默认线程。每个Python进程中的主线程总是名为“MainThread”，并且不是守护线程。一旦主线程退出，Python进程也将退出，前提是没有其他非守护进程在运行

通过在主线程内调用`threading.current_thread()`函数来表示主线程的线程实例

```
from threading import current_thread
thread = current_thread()
print(f'name={thread.name}, daemon={thread.daemon}, id={thread.ident}')
# name=MainThread, daemon=False, id=9072
```

通过调用`threading.main_thread()`函数获取主线程的线程实例

```
from threading import main_thread
thread = main_thread()
print(f'name={thread.name}, daemon={thread.daemon}, id={thread.ident}')
```

#### 线程应用函数

在Python进程中处理线程时，有许多实用程序可以使用

通过`threading.active_count()`函数实现可以发现Python进程中活动线程的数量。该函数返回一个整数，表示“活着”的线程数。

```
from threading import active_count
count = active_count()
print(count) # 1
```

通过`threading.current_thread()` 返回运行当前代码的线程的线程实例

```
from threading import Thread
from threading import current_thread

def task():
    thread = current_thread()
    print(thread.name)

thread = Thread(target=task)
thread.start()
thread.join()
```

通过`threading.get_ident()`函数，获得当前线程的Python线程标识符

```
from threading import get_ident
identifier = get_ident()
print(identifier)
```

通过`get_native_id()` 函数获得由操作系统分配的当前线程的本机线程标识符

```
from threading import get_native_id
identifier = get_native_id()
print(identifier)
```

通过`threading.enumerate()`函数可以获得Python进程中所有活动线程的列表。只有那些“活着”的线程才会包含在列表中，这意味着那些当前正在执行它们的run()函数的线程。

```
import threading
threads = threading.enumerate()
for thread in threads:
    print(thread.name)
```

#### 线程本地数据

线程可以通过线程的**threading.local**实例类存储本地数据。线程不能访问或读取其他线程的本地数据。每个线程必须挂起“本地”实例才能访问存储的数据

```
local = threading.local()
local.custom = 33
```

```
from time import sleep
import threading
 
def task(value):
    local = threading.local()
    local.value = value
    sleep(value)
    print(f'Stored value: {local.value}')
 
threading.Thread(target=task, args=(1,)).start()
threading.Thread(target=task, args=(2,)).start()
```

共享线程本地实例，我们可以创建线程本地对象的实例，并在多个线程之间共享。每个线程可以在相同的线程本地中使用相同的名称存储唯一的数据，而不会相互干扰

```
from time import sleep
import threading
 
def task(value, local):
    local.value = value
    sleep(value)
    print(f'Stored value: {local.value}')
 
# 创建一个共享的线程本地实例
local = threading.local()
threading.Thread(target=task, args=(1,local)).start()
sleep(0.5)
threading.Thread(target=task, args=(2,local)).start()
#输出
Stored value: 1
Stored value: 2
```

从输出表明，当线程本地实例在多个线程之间共享，并且每个线程存储针对同一属性的数据时，该属性对每个线程都是私有的

将线程局部实例作为全局变量并在每个函数中直接访问它来实现相同的结果

```
def task(value):
    global local
    local.value = value
    sleep(value)
    print(f'Stored value: {local.value}')


local = threading.local()
threading.Thread(target=task, args=(1,)).start()
sleep(0.5)
threading.Thread(target=task, args=(2,)).start()
```

这为必须将线程本地实例传递给需要访问线程本地数据的线程执行的每个函数提供了一种有用的替代方法

#### 互斥锁lock

互斥锁用于保护代码的关键部分不被并发执行。在Python中通过**threading.Lock**使用互斥锁

互斥锁是用于防止竞争条件的同步原语，竞态条件是指当两个线程运行相同的代码并访问或更新相同的资源(例如数据变量、流等)时，使资源处于未知和不一致的状态。竞争条件经常导致程序的意外行为和/或破坏数据，使用一个互斥锁来确保一次只有一个线程执行代码的关键部分,而所有其他线程试图执行相同的代码必须等到当前执行的线程完成关键部分和释放锁

- **Unlocked** 锁还没有被获取，可以由下一个尝试的线程获取。

- **Locked**一个线程已经获取了锁，任何试图获取锁的线程必须等待锁被释放

在任何时候，只有一个线程可以拥有锁。如果线程没有释放获得的锁，就不能再次获得它。

试图获取锁的线程将被阻塞，直到锁被获取。通过将" blocking "参数设置为False来尝试在不阻塞的情况下获取锁。如果无法获取锁，则返回False

```
lock.acquire(blocking=false)
```

还可以尝试使用超时来获取锁，该超时将等待设置的秒数来获取锁，然后放弃。如果无法获取锁，则返回False

```
lock.acquire(timeout=10)
```

也可以通过上下文管理器协议通过with语句使用锁，允许临界区在使用锁的过程中成为一个块

```
lock = Lock()
# 获得锁
with lock:
    # ...
```

这是推荐的用法，因为它明确了受保护代码的开始和结束位置，并确保锁总是被释放，即使在临界区中出现了异常或错误

可以通过locked()函数检查当前线程是否获取了锁`if lock.locked()`

```
from time import sleep
from random import random
from threading import Thread
from threading import Lock

def task(lock, identifier, value):
    with lock:
        print(f'>线程{identifier}获得了锁，休眠{value}  ')
        sleep(value)

# 创建共享锁
lock = Lock()
for i in range(10):
    Thread(target=task, args=(lock, i, random())).start()
```

#### 重入互斥锁Rlock

重入锁”，类似于互斥锁，只是它允许一个线程多次获得锁。由于许多原因，一个线程可能需要多次获得同一个锁

每次线程获得锁时，它也必须释放锁，这意味着拥有锁的线程有递归的获取和释放级别。因此，这种类型的锁有时被称为“递归互斥锁”。

线程可以在访问临界区之前创建RLock实例，并在临界区结束后释放RLock实例,  同lock

```
lock = RLock()
lock.acquire()
# ...
lock.release()
```

```
...
def report(lock, identifier):
    # 获得锁
    with lock:
        print(f'>线程 {identifier} 完成')

# work function
def task(lock, identifier, value):
    # 获得锁k
    with lock:
        print(f'>线程 {identifier} 等待 {value}')
        sleep(value)
        report(lock, identifier)

lock = RLock()
for i in range(10):
    Thread(target=task, args=(lock, i, random())).start()
```

#### 线程条件Condition

一个条件允许线程等待并得到通知。在并发中，一个条件(也称为监视器)允许多个线程收到关于某些结果的通知。它结合了互斥锁(mutex)和条件变量

互斥允许可以用来保护临界区，但不能用来警告其他线程某个条件已经改变或满足

线程可以获得一个条件(比如互斥)，然后它可以等待另一个线程通知它发生了变化。在等待过程中，线程被阻塞，并释放锁以供其他线程获取。然后，另一个线程可以获取条件、进行更改，并通知等待条件发生更改的一个线程、所有线程或子集。然后等待的线程可以唤醒(由操作系统安排)，重新获取条件(互斥锁)，检查任何已更改的状态并执行所需的操作

这强调了条件在内部使用互斥锁(获取/释放条件)，但它还提供了其他特性，比如允许线程等待该条件，并允许线程通知其他线程等待该条件。

我们可以创建一个条件对象，默认情况下，它会创建一个新的可重入互斥锁(`threading.RLock`类)将在内部使用

```
condition = threading.Condition()
```

我们可能有一个可重入的互斥锁或一个不可重入的互斥锁。但是不建议这样做，除非您知道您的用例有此需求。陷入麻烦的可能性很高

```
condition = threading.Condition(lock=my_lock)
```

为了让线程利用这个条件，它必须获取它并释放它，就像互斥锁一样

```
condition.acquire()
# 等待通知
condition.wait()
condition.release()
或者
with condition:
    # 等待通知
    condition.wait()
```

可以通过notify()函数通知一个等待的线程

```
with condition:
    # 通知一个等待的线程
    condition.notify()
```

一旦被通知的线程可以在条件中重新获得互斥锁，它就会停止阻塞。这将作为对wait()的调用的一部分自动尝试，您不需要做任何额外的操作

如果有多个线程在等待该条件，我们将不知道哪个线程将被通知，我们可以通过notify_all()函数通知所有等待条件的线程

```
from time import sleep
from threading import Thread
from threading import Condition
 
# task函数将接受条件对象和一个可存储数据的列表。该函数将阻塞一段时间，向列表添加数据，然后通知等待的线程
def task(condition, work_list):
    sleep(1)
    work_list.append(33)
    # 通知一个等待的线程工作已经完成
    print('线程发送通知...')
    with condition:
        condition.notify()
 
condition = Condition()
work_list = list()
print('等待数据的主线程...')
with condition:
    worker = Thread(target=task, args=(condition, work_list))
    worker.start()
    condition.wait()
print(f'获取数据: {work_list}')
```

下面实例主线程会阻塞一段时间，然后通知所有等待的线程（notify_all）它们可以开始处理了

task函数将获取条件并等待通知。一旦收到通知，它将生成一个介于0和1之间的随机值，阻塞该分数秒，然后报告该值

主线程会阻塞一秒钟，然后通知所有等待的线程，等待这些线程完成

```
from time import sleep
from random import random
from threading import Thread
from threading import Condition
 
def task(condition, number):
    # 等待通知
    print(f'线程 {number} 等待中...')
    with condition:
        condition.wait()
    value = random()
    sleep(value)
    print(f'线程 {number} 值 {value}')
 
condition = Condition()
# 启动一组等待通知的线程  
for i in range(5):
    worker = Thread(target=task, args=(condition, i))
    worker.start()
sleep(1)
# 通知所有等待的线程它们可以运行
with condition:
    # 等待的线程被通知
    condition.notify_all()
```

首先运行这个示例创建了5个线程，它们立即开始运行，所有线程都获得条件并阻塞等待通知。主线程阻塞一会，然后通知所有五个等待的线程。等待线程唤醒，每次获取一个状态下的锁，执行它们的处理并报告它们的结果



在条件中使用wait_for()函数。这个函数接受一个可调用对象，比如没有参数的函数或lambda表达式。调用wait_for()函数的线程将阻塞，直到收到通知，作为参数传入的可调用对象将返回True值。这可能意味着线程会被不同的线程多次通知，但只有在满足可调用对象中的条件时才会解除阻塞并继续执行

```
from time import sleep
from random import random
from threading import Thread
from threading import Condition

def task(condition, work_list):
    with condition:
        value = random()
        sleep(value)
        work_list.append(value)
        print(f'线程 添加 {value}')
        condition.notify()

condition = Condition()
work_list = list()
for i in range(5):
    worker = Thread(target=task, args=(condition, work_list))
    worker.start()
# 等待所有线程将其工作添加到列表中  
with condition:
    condition.wait_for(lambda: len(work_list) == 5)
    print(f'完成 : {work_list}')
```

运行该示例首先启动5个线程，每个线程将获取条件，生成一个随机值，将其添加到共享工作列表中，并通知主线程。主线程等待这个条件，并在每次一个新线程完成时收到通知，但实际上不会继续并打印消息，直到lambda可调用对象返回True(即列表中的值数量匹配线程数量)

如果第一个线程在第二个线程调用notify()之后调用wait()，那么它将不会被通知，而是永远等待。如果操作系统进行了上下文切换，允许第二个调用notify()的线程在第一个调用wait()的线程之前运行，则可能会发生这种情况



#### 线程信号量Semaphore

信号量本质上是一个受互斥锁保护的计数器，用于限制可以访问资源的线程数量。信号量是一种并发原语，它允许限制可以获得保护临界区锁的线程数量

它是互斥(mutex)锁的扩展，它增加了在其他线程阻塞之前可以获得该锁的线程数。一旦信号量满了，新线程只能在持有该信号量的现有线程释放一个位置后才能获得该信号量的位置

在内部，信号量维护一个受互斥锁保护的计数器，每次获取信号量时互斥锁递增，每次释放信号量时互斥锁递减。当创建信号量时，将设置计数器的上限。如果它被设置为1，那么信号量将像互斥锁一样工作

信号量提供了一个有用的并发工具，用于限制可以并发访问资源的线程数量。一些例子包括:

- 限制到服务器的并发套接字连接
- 限制硬盘上并发文件操作。
- 限制了并行计算。

**threading.Semaphore**实例必须在创建时进行配置，以设置内部计数器的限制。这个限制将与可以保存信号量的并发线程数匹配

```
# 创建一个限制为100的信号量
semaphore = Semaphore(100)
```

在这个实现中，每次获取信号量时，内部计数器就会递减。每次释放信号量，内部计数器就会增加。如果信号量没有可用的位置，则不能获取信号量。在这种情况下，试图获取信号量的线程必须阻塞，直到有可用的位置

通过调用acquire()函数来获取信号量。默认情况下，它是一个阻塞调用，这意味着调用线程将阻塞，直到信号量上有可用的位置为止，通过参数`blocking`指定不阻塞`semaphore.acquire(blocking=False)`, 通过参数`timeout`指定超时时间`semaphore.acquire(timeout=10)`，一旦获取信号量，就可以通过调用release()函数再次释放信号量

```
from time import sleep
from random import random
from threading import Thread
from threading import Semaphore
 
def task(semaphore, number):
    # 尝试获取信号量
    with semaphore:
        value = random()
        sleep(value)
        print(f'线程 {number} 值为 {value}')
 
semaphore = Semaphore(2)
for i in range(10):
    worker = Thread(target=task, args=(semaphore, i))
    worker.start()
```

所有10个线程都试图获取信号量，但一次只有两个线程被授予位置。信号量上的线程执行它们的工作，并在完成后按随机间隔释放信号量。每次释放信号量(通过上下文管理器)都允许另一个线程获取一个位置并执行其计算，同时每次只允许处理其中两个线程，即使所有10个线程都在执行它们的run方法

#### 线程事件event

事件是一个简单的并发原语，允许线程之间进行通信

一个`threading.Event`对象包装了一个布尔变量，该变量可以是“设置”(True)或“未设置”(False)。共享事件实例的线程可以检查事件是否被设置、设置事件、清除事件(使其不设置)或等待事件被设置

`threading.Event`提供了一种简单的方法，可以在充当动作触发器的线程之间共享布尔变量

```
event = threading.Event() # 创建一个事件实例
event.set() # 通过set()函数设置事件。等待要设置的事件的任何线程都将收到通知
event.is_set() #通过is_set()函数检查事件是否被设置，如果事件被设置，该函数将返回True，否则返回False
event.clear() # 以通过clear()函数将事件标记为“未设置”(无论当前是否设置)
event.wait() # 可以通过wait()函数等待事件的设置。调用此函数将阻塞，直到事件被标记为set(例如，另一个线程调用set()函数)。如果事件已经设置，wait()函数将立即返回
event.wait(timeout=10) # 返回的值为False表示未设置事件且调用超时
```

```
from time import sleep
from random import random
from threading import Thread
from threading import Event
 
def task(event, number):
    # 等待事件被设置
    event.wait()
    value = random()
    sleep(value)
    print(f'线程 {number} 值为 {value}')
 
# 创建一个共享事件对象
event = Event()
for i in range(5):
    thread = Thread(target=task, args=(event, i))
    thread.start()
print('主线程阻塞...')
event.clear() # 清除所有事件
sleep(2)
# 在所有线程中开始处理
event.set()
```

主线程阻塞了一会儿，允许所有线程启动并开始等待事件。主线程然后设置事件。这将触发执行处理并报告消息的所有5个线程

#### 线程定时器

**threading.Timer**是**threading.Thread**类的扩展，这意味着我们可以像使用普通线程实例一样使用它。

可以创建一个定时器实例并配置它。这包括执行前等待的时间(以秒为单位)、函数一旦被触发就要执行，以及目标函数的任何参数

```
timer = Timer(10, task, args=(arg1, arg2))
```

一旦创建，线程必须通过调用start()函数来启动，该函数将启动计时器

```
timer.start()
timer.cancel() # 决定在目标函数执行之前取消计时器，可以通过调用cancel()函数来实现
```

```
from threading import Timer
 
def task(message):
    print(message)
 
timer = Timer(3, task, args=('Hello world',))
timer.start()
print('等待计时器...')
# 输出
等待计时器...
Hello world
```



#### 线程屏障Barrier

它允许多个线程等待同一个barrier对象实例(例如，在代码中的同一点)，直到预定义的固定数量的线程到达(例如，barrier已满)，然后通知所有线程并释放它们继续执行

在内部，barrier维护等待barrier的线程数的计数和预期的最大当事方(线程)的配置。一旦预期的参与方数量达到预定义的最大数量，将通知所有等待线程

这提供了一种有用的机制来协调多个线程之间的操作

```
barrier = threading.Barrier(10) # 指定在barrier解除之前必须到达的参与方(线程)的数量
```

我们还可以在所有线程到达barrier时执行一个动作，这个动作可以通过构造函数中的`action`参数指定。

这个动作必须是可调用的，比如不接受任何参数的函数或lambda，并且在所有线程到达barrier之后，但在线程被释放之前，由一个线程执行

```
barrier = threading.Barrier(10, action=my_function)
```

设置一个默认超时，供所有到达barrier的线程使用，并调用wait()函数

```
barrier = threading.Barrier(10, timeout=5)
```

一旦配置好，barrier实例就可以在线程之间共享和使用。例如，线程可以通过wait()函数到达并等待barrier

```
barrier.wait()
```

这是一个阻塞调用，将在所有其他线程(预配置的参与方数量)到达屏障后返回

wait函数确实返回一个整数，表示等待到达障碍物的人数。如果一个线程是最后一个到达的线程，那么返回值将为0。如果您希望最后一个线程或一个线程在屏障释放后执行一个操作，这是在构造函数中使用“action”参数的一种替代方法，那么这是很有帮助的

```
remaining = barrier.wait()
if remaining == 0:
    print('I was last...')
```

可以通过`timeout`参数在调用中设置`timeout`为秒级等待。如果超时在所有参与方到达障碍之前过期，将在所有等待障碍的线程中引发`BrokenBarrierError`，障碍将被标记为破碎

```
try:
    barrier.wait()
except BrokenBarrierError:
    # ...
```

中止barrier意味着所有通过wait()函数等待barrier的线程将引发BrokenBarrierError，而barrier将被置于破碎状态

```
barrier.abort()
```

可以通过调用reset()函数来修复障碍并使其再次可用。如果您取消了协调工作，但希望使用相同的barrier实例再次重试

```
barrier.reset()
```

最后，屏障的状态可以通过属性来检查

- **parties** 报告配置的必须达到屏障的参与方数量
- **n_waiting** 报告在屏障上等待的当前线程数
- **broken** 属性表示屏障当前是否被打破

```
from time import sleep
from random import random
from threading import Thread
from threading import Barrier
 
def task(barrier, number):
    value = random() * 10
    sleep(value)
    print(f'线程 {number} 完成, 值为: {value}')
    # 等待所有其他线程完成
    barrier.wait()
 
barrier = Barrier(5 + 1)
for i in range(5):
    worker = Thread(target=task, args=(barrier, i))
    worker.start()
print('等待所有结果的主线程...')
barrier.wait()
print('所有线程都有它们的结果')
```

每个工作线程执行它的计算，然后在barrier上等待所有其他线程完成

对示例进行更新，以使用超时。具体来说，主线程可以等待固定的秒数让所有线程完成。如果所有线程都在规定时间内完成，则说明一切正常，否则我们就会报告不是所有工作都能按时完成

```
...
def task(barrier, number):
    value = random() * 10
    sleep(value)
    print(f'线程 {number} 完成, 值为: {value}')
    try:
        barrier.wait()
    except BrokenBarrierError:
        pass
 
barrier = Barrier(5 + 1)
for i in range(5):
    worker = Thread(target=task, args=(barrier, i))
    worker.start()
print('等待所有结果的主线程...')
try:
    barrier.wait(timeout=5)   # 为所有工作线程设置5秒的等待超时
    print('所有线程都有结果')
except BrokenBarrierError:
    print('有些线程没有按时完成...')
```

在这个特定的运行中，到达超时并打破障碍。所有等待的工作线程都会引发BrokenBarrierError，该错误将被忽略并终止线程。所有尚未到达barrier的工作线程都将到达barrier，引发BrokenBarrierError并终止

`action`用例，因为主线程不再需要等待barrier，我们可以将到达barrier的预期参与方的数量减少到5个，以匹配5个工作线程

```
def report():
    print('所有线程都有它们的结果')

def task(barrier, number):
    value = random() * 10
    sleep(value)
    print(f'线程 {number} 完成, 值为: {value}')
    barrier.wait()
 
barrier = Barrier(5, action=report)
for i in range(5):
    worker = Thread(target=task, args=(barrier, i))
    worker.start()
```

创建并启动五个工作线程，执行它们的计算并到达barrier，一旦所有线程都到达barrier, barrier将确保动作由其中一个工作线程触发，调用我们配置的report()函数一次。相比于第一个例子中尝试在主线程中做同样的事情，这是一个更干净的解决方案(更少的代码)，在障碍解除后执行一个动作，

`Aborting `由于某些原因，我们可能想要中止barrier上线程的协调。这可能是因为其中一个线程无法执行其所需的任务

我们可以通过调用abort()函数中止barrier，这将导致所有等待barrier的线程引发BrokenBarrierError，而所有新的调用者wait()也会引发相同的错误，这意味着所有对wait()的调用都应该由try-except结构来保护

更新第一个使用barrier的示例，以支持终止barrier。我们将在线程处理任务中添加一个检查，如果遇到关于协调工作的值大于8，则继续

```
def task(barrier, number):
    value = random() * 10
    sleep(value)
    print(f'线程 {number} 完成, 值为: {value}')
    # 检查结果
    if value > 8:
        print(f'线程 {number} 中止...')
        barrier.abort()
    else:
        try:
            barrier.wait()
        except BrokenBarrierError:
            pass
 
barrier = Barrier(5 + 1)
for i in range(5):
    worker = Thread(target=task, args=(barrier, i))
    worker.start()
print('等待所有结果的主线程...')
try:
    barrier.wait()
    print('所有线程都有它们的结果')
except BrokenBarrierError:
    print('至少有一个线程由于不良结果而中止  .')
```

每个线程执行其处理，并根据生成的特定随机数有条件地尝试中止或等待barrier

#### 线程异常处理

如果未处理的异常可能发生在新线程中，其结果是，线程将展开并在出现标准错误时报告消息，展开线程意味着线程将在异常(或错误)处停止执行，并且异常将在线程堆栈中冒泡，直到达到顶层，例如run()函数

我们可以通过异常钩子指定如何处理在新线程中发生的未处理错误和异常。默认情况下，没有异常钩子，在这种情况下调用`sys.Excepthook`函数来报告熟悉的消息。

我们可以指定一个自定义异常钩子函数，它将在线程执行时被调用当一个**threading.Thread** 因为未处理的错误或者异常而失败

首先，必须定义一个函数，该函数接受一个参数，该参数将是ExceptHookArgs类的实例，包含异常和线程的详细信息。然后，我们可以指定当未处理的异常冒泡到线程的顶层时调用的异常挂钩函数。

```
from time import sleep
import threading

def work():
    sleep(1)
    raise Exception('Something bad happened')

def custom_hook(args):
    print(f'Thread failed: {args.exc_value}')

threading.excepthook = custom_hook
thread = threading.Thread(target=work)
thread.start()
thread.join()
print('Continuing on...')
```

#### Python线程处理最佳实践

在Python中使用线程的一些最佳实践如下

- 使用上下文管理器： 上下文管理器的好处是，锁总是在块退出后立即释放，而不管它是如何退出的，例如，正常情况下是返回、错误或异常
- 在等待时使用超时：这将允许等待线程在固定的时间限制后放弃等待，然后尝试纠正这种情况，例如报告错误，强制终止等
- 使用互斥锁来保护临界区： 一个临界区可能指的是一个代码块，但它也指的是多个函数对同一数据变量或资源的多次访问。使用一个互斥锁来确保一次只有一个线程执行代码的关键部分,而所有其他线程试图执行相同的代码必须等到当前执行的线程完成关键部分和释放锁。
- 有序获取锁

#### Python线程常见错误

- 竞态条件

  - 带有变量的竞态条件
  - 带定时的竞争条件

- 线程死锁： 死锁是一种并发失败模式，其中一个或多个线程等待一个永远不会发生的条件。结果是死锁线程无法继续，程序被卡住或冻结，必须强制终止

  - 一个等待自己的线程(例如，试图获得同一个互斥锁两次)

    ```
    def task(lock):
        print('获取锁...')
        with lock:
            print('线程再次获取锁...')
            with lock:
                pass
    ```

    ```
    def task2(lock):
        print('线程再次获取锁...')
        with lock:
            pass
     
    def task1(lock):
        print('获取锁...')
        with lock:
            task2(lock)
    
    lock = Lock()
    thread = Thread(target=task1, args=(lock,))
    # 线程在task1()中获得锁，模拟一些工作，然后调用task2()。task2()函数试图获取相同的锁，线程陷入死锁，等待自己释放锁，以便再次获取锁
    ```

  - 相互等待的线程(例如A等待B, B等待A)

    ```
    def task(other):
        print(f'[{current_thread().name}] waiting on [{other.name}]...')
        other.join()
     
    main_thread = current_thread()
    new_thread = Thread(target=task, args=(main_thread,))
    new_thread.start()
    task(new_thread)
    # [Thread-1] waiting on [MainThread]...
    # [MainThread] waiting on [Thread-1]...
    ```

  - 释放资源失败的线程(例如互斥锁、信号量、屏障、条件、事件等)

  - 以不同的顺序获得互斥锁的线程(例如，无法执行锁顺序)。

- 线程活动锁: 一个线程没有被阻塞，但由于另一个线程的操作而无法进行。线程可能同时尝试获取一个锁或一系列锁，检测到它们正在竞争相同的资源，然后退回。这个过程是重复的，两个线程都不能继续，因此被“锁定”。活锁和死锁之间的主要区别是线程(或多个线程)在无法进展时的状态。 线程无法取得进展，但可以继续执行代码。

  ```
  def task(number, lock1, lock2):
      while True:
          with lock1:
              sleep(0.1)
              if lock2.locked():
                  print(f'Task {number} cannot get the second lock, giving up...')
              else:
                  with lock2:
                      print(f'Task {number} made it, all done.')
                      break
   
  lock1 = Lock()
  lock2 = Lock()
  thread1 = Thread(target=task, args=(0, lock1, lock2))
  thread2 = Thread(target=task, args=(1, lock2, lock1))
  thread1.start()
  thread2.start()
  thread1.join()
  thread2.join()
  ```

  

#### Python线程常见问题

**如何停止线程?**

通过event.set(),  任务循环检查每次迭代的事件状态(is_set)，如果设置为中断任务循环

```
def task(event):
    for i in range(5):
        sleep(1)
        if event.is_set():
            break
        print('工作线程运行...')
    print('工作线程关闭')
 
event = Event()
thread = Thread(target=task, args=(event,))
thread.start()
sleep(3)
print('主线程停止')
event.set()
thread.join()
```

**如何杀死一个线程?**

- Control-C命令

- Control-\命令

- kill命令并指定进程id

**如何等待线程完成?**

`thread.join()`  这将阻塞当前线程，直到已连接的目标线程终止, 也可以指定超时时间

```
thread.join(timeout=10)
# 检查目标线程是否仍在运行
if thread.is_alive():
	# 超时已过，线程仍在运行
else:
	# 线程终止
```

**如何重启一个线程?**

不能重新启动或重用Python线程。事实上，这可能是底层操作系统提供的线程功能的一个限制。一旦线程终止，就不能再对其调用start()方法来重用它

**如何在Python中使用倒计时锁?**

Python没有提供倒计时锁，但我们可以使用新类和threading.Condition轻松地开发倒计时锁。

开发一个简单的倒计时锁类CountDownLatch。它必须有三个元素

- **Constructor** 需要一个计数并初始化内部锁
- **CountDown** 这将以线程安全的方式减少计数器，并在计数器达到0时通知等待的线程
- **Wait** 这允许线程阻塞，直到计数达到0

```
class CountDownLatch():
    # constructor
    def __init__(self, count):
        self.count = count
        # 控制访问计数和通知锁闩是打开的  
        self.condition = Condition()
 
    # 锁存器每增加一个数
    def count_down(self):
        # acquire the lock on the condition
        with self.condition:
            # 检查门闩是否已经打开
            if self.count == 0:
                return
            # 减少计数器
            self.count -= 1
            # 检查门闩是否打开
            if self.count == 0:
                # 通知所有等待线程闩锁已打开 
                self.condition.notify_all()
 
    # 等门闩打开
    def wait(self):
        # 在条件下获取锁
        with self.condition:
            # 检查门闩是否已经打开
            if self.count == 0:
                return
            self.condition.wait()  # 等待通知

latch = CountDownLatch(5)

```

**如何从一个线程等待一个结果?**

- 在扩展的threading.Thread上使用实例变量。
- 使用一个队列。在线程之间共享结果的队列
- 使用全局变量在线程之间共享结果

**如何修改上下文切换间隔?**

在多任务操作系统中，上下文切换包括暂停一个线程的执行和恢复另一个线程的执行。并非所有线程都能够同时运行。相反，操作系统通过允许每个线程运行一小段时间来模拟多任务，然后暂停线程的执行并存储其状态并切换到另一个线程

挂起一个线程并重新激活挂起的线程的过程称为上下文切换。
Python中的切换间隔指定Python解释器允许一个Python线程在被迫为上下文切换可用之前运行多长时间

Python 3提供了一个API，允许您将上下文切换间隔设置为以秒为单位的时间间隔。缺省值为5毫秒，即为0.005秒。

```
value = sys.getswitchinterval()
sys.setswitchinterval(1.0)  # 设置间隔
```

改变值有两个主要原因，它们是:

- 允许线程在切换之前运行更长时间以提高性能，例如增加值
- 在一个开关暴露竞争条件之前，允许线程运行更少的时间，例如减少值

**如何休眠一个线程?**

用`sleep()`函数将导致调用线程阻塞指定的秒数

```
time.sleep(5)
```

**随机数线程安全吗?**

Python中的随机模块基本上是线程安全的。(python3.10)

具体来说，所有随机数的生成都依赖于random.random()函数，该函数调用C-code，是线程安全的。

非线程安全的随机类是gauss()函数，特别是`Random.gauss()`和`Random.Random.gauss()`。因此，应该在多线程应用程序中使用`random.normalvariate()`函数，或者，可以使用互斥锁通过线程保护random.gauss()函数

**列表、字典和集合是线程安全的吗?**

是的。原子操作是一个或一系列不间断完成的代码指令。线程不能在原子操作的中间进行上下文切换。
这意味着这些操作是线程安全的，因为我们可以预期它们一旦启动就会完成

Python内置数据结构（int、list、dicts等)上的大多数操作都是原子的，因此是线程安全的

**日志记录线程安全?**

是的。日志记录是在程序中跟踪事件的一种方法。日志记录模块可以直接在多个线程中使用。这是因为日志记录模块是线程安全的。这是通过使用锁实现的。在内部，日志模块使用互斥锁，以确保日志处理程序免受多个线程的竞争条件的影响

**需要检查`__main__`吗**

不需要。当通过threading.Thread在Python中使用线程时，不需要检查`__main__`。

在Python中通过`multiprocessing.process`使用进程时，需要检查`__main__`。

**Python有Volatile变量吗?**

没有。在并发编程中，Volatile变量指的是每次访问时都必须从主存中检索其值的变量。这就是现代编译性编程语言(如Java和c#)中使用的“volatile”的含义。在这些语言中，虚拟机可以在每个线程或堆栈空间中维护变量值的缓存副本。Python没有volatile变量。

**什么是线程繁忙等待?**

忙碌等待，也称为旋转，是指一个线程在循环中反复检查一个条件

被称为“忙碌”或“旋转”，因为线程继续执行相同的代码，例如while循环中的if语句，通过执行代码实现等待(例如保持忙碌)

在并发编程中，繁忙等待通常是不可取的，因为检查条件的紧密循环不必要地消耗CPU周期，占用CPU核心。因此，它有时被称为并发编程的反模式，一种应该避免的模式

也就是说，在某些情况下，繁忙等待是首选的解决方案，例如，由于不可预测的执行时间或竞争条件，线程之间的通信或信号可能会被错过。在这种情况下，繁忙等待可以提供一种替代其他并发原语的方法。

**什么是线程自旋锁**

自旋锁是对互斥锁的繁忙等待。自旋锁是一种锁类型，如果线程已经被锁定，则它必须执行繁忙等待

```
while True:
    acquired = lock.acquire(blocking=False)
    if acquired:
        # stop waiting
        break
```

我们可以看到，繁忙循环将一直循环下去，直到获得锁。每次循环迭代时，我们都尝试在不阻塞的情况下获取锁。如果被获取，循环将退出

```
lock.acquire()
```

我们可以将上述自旋锁的繁忙等待循环与简单地阻塞直到锁可用的交替进行对比。在这种情况下，等待线程在等待锁时无法执行任何其他操作。自旋锁的一个限制是重复执行一个紧密循环增加的计算负担

繁忙等待循环的计算负担可以通过添加阻塞睡眠来减少，例如，对time.sleep()的调用可以持续几分之一秒

```
while True:
    acquired = lock.acquire(blocking=False)
    if acquired:
        break
    else:
    	sleep(0.1)
```

或者，尝试在每次循环迭代中获取锁，可以使用一个短的阻塞等待，超时时间为几分之一秒

```
while True:
    acquired = lock.acquire(timeout=0.1)
    if acquired:
        break
```

这两种方法都将减少繁忙循环的迭代次数，导致大部分执行时间花费在睡眠或阻塞上。这将允许操作系统上下文切换线程，并可能释放CPU核心。

添加睡眠或阻塞等待的缺点是，它可能会在锁变得可用和线程注意到这一事实并获得它之间引入延迟。这种延迟的容忍度将取决于应用程序。

**如何创建线程安全的计数器?**

通过使用互斥锁(互斥锁)**threading.Lock** 类，可以使计数器成为线程安全的。

```
class ThreadSafeCounter():
    def __init__(self):
        self._counter = 0
        # 初始化锁
        self._lock = Lock()
    # 增加计数
    def increment(self):
        with self._lock:
            self._counter += 1
    # 获取计数器值
    def value(self):
        with self._lock:
            return self._counter
```

**Python线程是“真正的线程”吗?**

是的。 Python使用真正的系统级线程，也称为内核级线程，这是Windows、Linux和MacOS等现代操作系统提供的功能

Python线程不是软件级线程，有时称为用户级线程或绿色线程

#### 其它

CPython Python解释器通常不允许同时运行一个以上的线程，这是通过解释器中的互斥(mutex)锁实现的，它确保在Python虚拟机中一次只能有一个线程执行Python字节码

没有GIL的第三方Python解释器

- Jython:用Java编写的开源Python解释器
- IronPython:一个用.net编写的开源Python解释器


