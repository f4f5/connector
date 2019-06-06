#  找到效率最优的socket写法

首先是一篇入门级的文章： https://realpython.com/python-sockets/  这篇文章主要写了python中socket编程的写法。介绍了阻塞式的写法和基于select的非阻塞式的。

之后是稍微更进一步的文章 https://cloud.tencent.com/developer/article/1373483 这篇文章述说了阻塞/异步等IO的基础知识，以及各操作系统在IO上的这些特点。以下是摘要：

>IO从概念上来说，总共有5种：
>
>（1）阻塞IO （blocking I/O）
>
>（2）非阻塞IO （nonblocking I/O）
>
>（3）IO多路复用 （I/O multiplexing (select and poll)）
>
>（4）事件驱动IO （signal driven I/O (SIGIO)）
>
>（5）异步IO (asynchronous I/O (the POSIX aio_functions))
>
>下面我们来看下select，poll，epoll，kqueue，iocp分别属于那种模型：
>
>select，poll属于第三种IO复用模型，iocp属于第5种异步io模型，那么epoll和kqueue呢？
>
>其实与select和poll一样，都属于第三种模型，只是更高级一些，可以看做拥有了第四种模型的某些特性，比如callback的回调机制。
>
>那么epoll，kqueue为什么比select和poll高级呢？ 下面我们来分析一下：
>
>首先他们都属于IO复用模型，I/O多路复用模型就是通过一种机制，一个进程可以监视多个描述符，一旦某个描述符就绪（一般是读就绪或者写就绪），能够通知程序进行相应的读写操作。
>
>select主要缺陷是，对单个进程打开的文件描述是有一定限制的，它由FD_SETSIZE设置，默认值是1024，虽然可以通过编译内核改变，但相对麻烦，另外在检查数组中是否有文件描述需要读写时，采用的是线性扫描的方法，即不管这些socket是不是活跃的，我都轮询一遍，所以效率比较低。
>
>poll本质和select没有区别，但其采用链表存储，解决了select最大连接数存在限制的问题，但其也是采用遍历的方式来判断是否有设备就绪，所以效率比较低，另外一个问题是大量的fd数组在用户空间和内核空间之间来回复制传递，也浪费了不少性能。
>
>epoll和kqueue是更先进的IO复用模型，其也没有最大连接数的限制(1G内存，可以打开约10万左右的连接)，并且仅仅使用一个文件描述符，就可以管理多个文件描述符，并且将用户关系的文件描述符的事件存放到内核的一个事件表中（底层采用的是mmap的方式），这样在用户空间和内核空间的copy只需一次。另外这种模型里面，采用了类似事件驱动的回调机制或者叫通知机制，在注册fd时加入特定的状态，一旦fd就绪就会主动通知内核。这样以来就避免了前面说的无脑遍历socket的方法，这种模式下仅仅是活跃的socket连接才会主动通知内核，所以直接将时间复杂度降为O(1)。
>
>最后来聊聊windows的iocp的异步IO模型，目前很少有支持asynchronous I/O的系统，即使windows上的iocp非常出色，但由于其系统本身的局限性和微软的之前的闭源策略，导致主流市场大部分用的还是unix系统，与mac系统的kqueue和linux系统的epoll相比，iocp做到了真正的纯异步io的概念，即在io操作的第二阶段也不阻塞应用程序，但性能好坏，其实取决于copy数据的大小，如果数据包本来就很小，其实这种优化无足轻重，而kqueue与epoll已经做得很优秀了，所以这可能也是unix或者mac系统至今都没有实现纯异步的io模型主要原因。
>


之后就是python的文档。在寻找中发现，asyncio这个python标准库中有对windows的IOCP模式进行处理。那么问题就来了，asyncio 在面对不同的操作系统时会自动的选择最优策略吗？它是基于select 的还是基于 epoll？ 
经过文档发现，采用 selectors.DefaultSelector 会使用平台上最优的selector。所以，在事件循环中，aysycio也是自己弄了最优的select。 当然，window平台的select本身性能就不行，所以得用另外的事件机制。文档是这样说的:


>asyncio ships with two different event loop implementations: SelectorEventLoop and ProactorEventLoop.
>
>By default asyncio is configured to use SelectorEventLoop on all platforms.
>
>## class asyncio.SelectorEventLoop
>> An event loop based on the selectors module.
>>
>>  Uses the most efficient selector available for the given platform. It is also possible to manually configure the exact selector implementation to be used:
```
>>> sl1=selectors.DefaultSelector()
>>> sl2=selectors.EpollSelector()
>>> repr(sl1)
'<selectors.EpollSelector object at 0x7f4135d33860>'
>>> repr(sl2)
'<selectors.EpollSelector object at 0x7f4135d33dd8>'
>>>

```
当然我们可以显式的执行：  
`asyncio.SelectorEventLoop(selectors.EpollSelector())`  
或者：  
`asyncio.SelectorEventLoop(selectors.KqueueSelector())`

在asyncio的源码可以看到：
```
class BaseSelectorEventLoop(base_events.BaseEventLoop):
    """Selector event loop.
    See events.EventLoop for API specification.
    """

    def __init__(self, selector=None):
        super().__init__()

        if selector is None:
            selector = selectors.DefaultSelector()
        logger.debug('Using selector: %s', selector.__class__.__name__)
        self._selector = selector
        self._make_self_pipe()
        self._transports = weakref.WeakValueDictionary()
```
DefaulSelector的文档描述如下：

>## class selectors.DefaultSelector
>
>The default selector class, using the most efficient implementation available on the current platform. This should be the default choice for most users.

ProactorEventLoop 的说明：

>## class asyncio.ProactorEventLoop
>
>An event loop for Windows that uses “I/O Completion Ports” (IOCP).
>
>Availability: Windows.
>
>An example how to use ProactorEventLoop on Windows:
>```
>    import asyncio
>    import sys
>
>    if sys.platform == 'win32':
>        loop = asyncio.ProactorEventLoop()
>        asyncio.set_event_loop(loop)
>```
>
所以，最终的答案将是：
```
import sys
import asyncio

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
else:
    loop = asyncio.get_event_loop()
    
asyncio.set_event_loop(loop)