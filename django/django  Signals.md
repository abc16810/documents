#### Signal

Django包含了一个“信号分派器”，它可以帮助解耦的应用程序在框架的其他地方发生动作时得到通知。简而言之，当event（事件）发生时，signals（信号）允许若干 senders（寄件人）通知一组 receivers（接收者）

Django提供了一组内置的信号，让用户代码得到Django自己的某些动作的通知。其中包括一些有用的通知- 

- [`post_save`](https://docs.djangoproject.com/en/4.0/ref/signals/#django.db.models.signals.post_save)   对象保存之后
- [`pre_save`](https://docs.djangoproject.com/en/4.0/ref/signals/#django.db.models.signals.pre_save)      对象保存之前
- [`post_delete`](https://docs.djangoproject.com/en/4.0/ref/signals/#django.db.models.signals.post_delete)   对象删除后
- [`pre_delete`](https://docs.djangoproject.com/en/4.0/ref/signals/#django.db.models.signals.pre_delete)    对象删除前
- [`m2m_changed`](https://docs.djangoproject.com/en/4.0/ref/signals/#django.db.models.signals.m2m_changed)   多对多对象更新时
- [`request_finished`](https://docs.djangoproject.com/en/4.0/ref/signals/#django.core.signals.request_finished)   完成HTTP请求时
- [`request_started`](https://docs.djangoproject.com/en/4.0/ref/signals/#django.core.signals.request_started)   当Django开始处理HTTP请求时

常用案例

- 通知类：通知是signal最常用的场景之一。例如，在博客中文章得到回复时，通知博主等
- 初始化：事件完成后，做一系列的初始化工作，如cmdb中添加一个资产后，ansible自动化收集相关硬件信息

#### 信号处理函数

要接收信号，请使用signal .connect()方法注册一个接收器函数。接收函数在信号发送时被调用。所有信号的接收函数都按照它们被注册的顺序一次调用一个

```
# Signal.connect(receiver, sender=None, weak=True, dispatch_uid=None)
# receiver -将连接到这个信号的回调函数
# sender - 指定接收信号的特定发送方
# weak - Django默认将信号处理程序存储为弱引用。因此，如果你的接收器是一个本地函数，它可能会被垃圾回收
# dispatch_uid - 在可能发送重复信号的情况下，信号接收器的唯一标识符


Signal.connect(func)
def func(sender, **kwargs):  
    pass
# 装饰器写法
from django.dispatch import receiver
@receiver(request_finished)
def func(sender, **kwargs):  
    pass
```

如下当一个请求开始打印`Request started!`  请求结束时打印`Request finished!`

```
from django.core.signals import request_started, request_finished
from django.dispatch import receiver

@receiver(request_started)
def my_callback(sender, **kwargs):
    print("Request started!")

@receiver(request_finished)
def my_callback(sender, **kwargs):
    print("Request finished!")
# 该段代码必须被django加载，一般通过apps.py 加载
class MyAppConfig(AppConfig):
    ...
    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from . import signals
```

**post_save**

```
@receiver(post_save, sender=MyModel)
def my_handle(sender, instance, created, **kwargs):
# sender  # The model class
# instance 正在保存的实际实例
# created 个布尔值;如果创建了新记录，则为True
# update_fields 传递给Model.save()时要更新的字段集合，或者如果update_fields没有传递给save()，则为None
```



#### 指定sender

有些信号被多次发送，但您只对接收这些信号的某个子集感兴趣，这个时候需要指定sender为特定模型，这个时候信号接收仅由特定sender发送方发送的信号

```
from django.db.models.signals import pre_save
from django.dispatch import receiver
from myapp.models import MyModel

@receiver(pre_save, sender=MyModel)
def my_handler(sender, **kwargs):
    ...
# my_handler函数只有在保存MyModel实例时才会被调用
```

#### 防止重复的信号

在某些情况下，连接接收器和信号的代码可能会运行多次。这可能导致您的receiver函数被注册多次，因此一个信号事件被调用多次。例如，ready()方法可以在测试期间执行多次。更常见的是，当项目导入定义信号的模块时，这种情况就会发生，因为信号注册会随着导入次数的增加而运行

比如当保存模型时使用信号发送邮件，传递一个唯一的标识符作为dispatch_uid参数来识别您的接收函数。这个标识符通常是一个字符串，尽管任何可哈希对象都可以。最终的结果是，对于每个唯一的dispatch_uid值，receiver函数将只绑定到信号一次

```
from django.core.signals import request_finished

request_finished.connect(my_callback, dispatch_uid="my_unique_identifier")
```



#### 自定义信号

```
from django.dispatch import Signal
custom_signal_test = Signal()  # 这声明了一个custom_signal_test信号

# 在需要调用的代码中发送信号
custom_signal_test.send(sender=self.__class__, instance=self.object, size=size)
```





