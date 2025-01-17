#### 主机选择

Kafka可以运行在最少1个核心和1GB的内存上，并根据数据保持的需求进行扩展。 CPU很少成为瓶颈，因为Kafka的I/O负担很重，但是具有足够线程的中等大小的CPU对于处理并发连接和后台任务仍然很重要

要运行具有最高性能的Kafka，最简单的建议是为Kafka代理提供专用的主机，为Kafka集群提供专用的ZooKeeper集群

- 不运行在虚拟机。 在现代数据中心中，在虚拟机中运行进程是一种常见的实践。这通常允许更好地共享资源。Kafka对I/O吞吐量非常敏感，以至于vm会干扰代理的正常操作。因此，强烈建议不要为Kafka使用VMs;如果您在虚拟环境中运行Kafka，您需要依赖VM供应商来帮助优化Kafka的性能。
- 在zookeeper和borkers下运行其他进程。 由于与其他进程存在I/O争用，通常建议避免在与Kafka代理相同的主机上运行其他此类进程。


#### 系统设置
- Kafka需要为文件和网络连接打开文件描述符,您应该将文件描述符限制设置为至少128000。
```
kafka   - nofile   128000
kafka   - nproc    65536
```
- 可以增加最大的套接字缓冲区大小，以支持高性能的数据传输。 设置比您定义的任何Kafka send 缓冲区都大的缓冲区大小

#### 文件系统选择
Kafka使用常规的Linux磁盘文件进行存储。我们建议使用EXT4或XFS文件系统。对XFS文件系统的改进显示了Kafka在不影响稳定性的情况下改进的性能特征。

不要使用挂载的共享驱动器或任何网络文件系统为Kafka，因为存在索引失败的风险和(在网络文件系统中)与使用memory mapping文件存储偏移索引相关的问题

Kafka不支持加密的文件系统，比如SafenetFS。可能会发生索引文件损坏。

使用`noatime`或`relatime`可以提升 ext2， ext3 及 ext4 格式磁盘的性能

```
/xxx/xx /opt/h2   xfs     defaults,noatime        0 0
```

#### 磁盘驱动器的考虑
对于吞吐量，我们建议将多个驱动器分配给Kafka数据。使用Kafka时，更多的驱动器通常比更少的表现更好。不要与任何其他应用程序共享这些Kafka驱动器，也不要将它们用于Kafka应用程序日志

你可以通过在`server.properties`文件中的`log.dirs`属性指定一个逗号分隔的目录列表，可以配置多个驱动器。kafka使用循环方法将分区分配到指定的目录`log.dirs`中。默认值是`/tmp/kafka-logs`。

#### raid
RAID可能会改进磁盘之间的负载平衡，但是由于写操作较慢，RAID可能会导致性能瓶颈。此外，它减少了可用的磁盘空间。尽管RAID可以容忍磁盘故障，但重建RAID阵列需要大量的I/O，并且会有效地禁用服务器。因此，RAID在可用性方面没有提供实质性的改进


#### 网络和IO线程配置优化
`num.io.threads`设置一个值，该值等于或大于为Kafka专用的磁盘数量。 建议 配置线程数量为cpu核数2倍，最大不超过3倍.

#### 日志刷新管理
 - 每当producer写入10000条消息时，刷数据到磁盘。`log.flush.interval.messages=10000`
 - 每间隔1秒钟时间，刷数据到磁盘。`log.flush.scheduler.interval.ms=1000`

我们建议使用默认的刷新设置，它依赖于Linux和Kafka完成的后台刷新。默认设置提供高吞吐量和低延迟，并且通过使用复制保证恢复。



#### 日志保留策略配置
- `log.retention.hours=168` 日志保留时间7天， 可以减少日志保留天数
- `log.segment.bytes` 指定日志文件的大小。当日志文件达到最大大小时，Kafka将日志文件刷新到磁盘。topic分区的日志存储为段文件目录。此设置控制在日志中滚动新段之前段文件的最大大小。默认为1GB即`log.segment.bytes=1073741824`


#### Broker 配置属性
- `message.max.bytes` 代理接收的最大消息大小 默认1000000 （1M）
- `log.segment.bytes` kafka数据文件的大小。必须大于任何单个消息。 默认 1073741824 (1 GiB)
- `replica.fetch.max.bytes` 代理可以复制的最大消息大小。必须大于`message.max.bytes` 否则broker可以接受它不能复制的消息，这可能导致数据丢失

#### Consumer 配置属性
- `max.partition.fetch.bytes` 返回每个分区的最大数据量 默认10485760 (10 MiB)
- `fetch.max.bytes` 服务器应该为获取请求返回的最大数据量。 默认52428800 (50 MiB)

#### JVM和垃圾收集
```
-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:+DisableExplicitGC -Djava.awt.headless=true \
-Xloggc:/var/log/kafka/kafkaServer-gc.log -verbose:gc -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+PrintGCTimeStamps
```
#### 虚拟内存处理
于Kafka来说，这是一个重要的内核参数，因为分配给交换空间的内存越多，分配给页面缓存的内存就越少。 建议设置`vm.swappiness`值为1

Kafka严重依赖于磁盘I/O性能 ：`vm.dirty_ratio和vm.dirty_background_ratio`内核参数是否控制脏页刷新到磁盘的频率。更高的`vm.dirty_ratio`导致较少的磁盘刷新。

显示系统中脏页的实际数目,运行`egrep "dirty|writeback" /proc/vmstat`

#### 网络参数
Kafka被设计用来处理大量的网络流量。默认情况下，Linux内核没有针对这种情况进行调优。以下内核设置可能需要根据用例或特定的Kafka工作负载进行调优
```
net.core.wmem_default: 默认发送套接字缓冲区大小。
net.core.rmem_default: 默认接收套接字缓冲区大小。
net.core.wmem_max: 最大发送套接字缓冲区大小。
net.core.rmem_max: 接收套接字缓冲区的最大大小。
net.ipv4.tcp_wmem: 为TCP发送缓冲区保留的内存。
net.ipv4.tcp_rmem: 为TCP接收缓冲区保留的内存。
net.ipv4.tcp_window_scaling: TCP窗口缩放选项。
net.ipv4.tcp_max_syn_backlog: 未完成的TCP SYN请求(连接请求)的最大数量。
net.core.netdev_max_backlog:内核输入端的最大排队包数(用于处理网络请求的峰值)。
```