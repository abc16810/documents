#### 时间同步

集群中的所有机器都需要具有相同的时间和日期设置，包括时区。强烈建议使用网络时间协议(NTP)。许多集群服务对时间非常敏感(例如HBase、Kudu、ZooKeeper)，如果所有主机的时间一致，故障排除就会非常容易。
```
# (RHEL/CentOS 6) 
service ntpd start 
chkconfig ntpd on 
# (RHEL/CentOS 7) 
systemctl start ntpd.service 
systemctl enable ntpd.service
```

#### 名称服务缓存
hosts文件解析 或者DNS服务器，如果使用DNS，建议开启nscd
nscd（Name Service Cache Daemon）是一种能够缓存 passwd、group、hosts 的本地缓存服务，分别对应三个源 /etc/passwd、/etc/hosts、/etc/resolv.conf。其最为明显的作用就是加快 DNS 解析速度，在接口调用频繁的内网环境建议开启
```
# hosts
192.168.10.1 master
192.168.10.2 node1
192.168.10.3 node2
```

#### 关闭SELinux
在启用了安全增强的Linux (SELinux)的平台上是受限支持的,建议在Hadoop集群的所有机器上禁用SELinux
```
# SELinux可以在RHEL/CentOS上禁用
vim /etc/sysconfig/selinux  # 配置如下
SELINUX=disabled
```

#### 禁用IPv6

Hadoop不支持IPv6。应该删除IPv6配置，停止与IPv6相关的服务。
```
# 编辑/etc/sysctl.conf  添加如下两行 禁用ipv6
net.ipv6.conf.all.disable_ipv6=1
net.ipv6.conf.default.disable_ipv6=1
```

#### 禁用防火墙

建议在集群上禁用基于主机的防火墙，至少在集群启动并运行之前是这样。许多难以诊断的问题都是由于不正确/冲突的iptables条目干扰了正常的集群通信造成的。执行以下操作将禁用IPv4和IPv6的iptables
```
# (RHEL/CentOS 6) 
service iptables stop 
service ip6tables stop 
chkconfig iptables off 
chkconfig ip6tables off 

# (RHEL/CentOS 7) 
systemctl stop firewalld.service 
systemctl disable firewalld.service
```

#### 禁用无用的服务

与任何生产服务器一样，应该删除和/或禁用未使用的服务。有些示例服务在默认情况下是打开的，而我们不需要它们

    • bluetooth
    • cups
    • iptables
    • ip6tables
    • postfix3

 要查看配置为在系统启动期间启动的服务的列表，请执行以下命令

```
 # (RHEL/CentOS 6) 
chkconfig –list | grep on 
# (RHEL/CentOS 7) 
systemctl list-unit-files --type service | grep enabled
```

#### 预留合适的内存
每个节点上的内存分配给各个Hadoop进程。这种可预测性降低了Hadoop进程无意中耗尽内存并分页到磁盘的可能性，从而导致性能严重下降

在操作系统和其他非hadoop使用的节点上，至少应该预留4 GB的内存。如果其他非hadoop应用程序在集群节点上运行，比如第三方活动监视/警报工具，那么这个数量可能需要更高


#### 禁用调优服务
如果您的集群主机正在运行RHEL/CentOS 7.x，通过运行以下命令禁用“tuned”服务

```
# 确保已调优的服务已启动
systemctl start tuned
# 关闭调优的服务
tuned-adm off
# 确保没有活动配置文件
tuned-adm list
No current active profile  #输出应该包含以下行
# 关闭并禁用调优的服务
systemctl stop tuned
systemctl disable tuned
```
#### 配置vm.swappiness

Linux内核参数vm.swappiness是一个0到100之间的值，它控制从物理内存到磁盘上的虚拟内存的应用程序数据(作为匿名页面)的交换。值越高，从物理内存中交换出的非活动进程就越频繁。值越低，交换的越少，强制清空文件系统缓冲区。

在大多数系统上，vm.swappiness默认设置为60。这不适用于Hadoop集群，因为即使有足够的内存可用，进程有时也会被交换。这可能会导致重要的系统守护进程出现长时间的垃圾收集暂停，从而影响稳定性和性能

建议您设置vm.swappiness值介于1和10之间，最好是1,在RHEL内核为2.6.32-642的系统或更高的系统上进行最小交换

```
sudo sysctl -w vm.swappiness=1
```

#### 禁用透明大页

Linux平台都包含一个称为透明hugepages的特性，该特性与Hadoop工作负载的交互很差，会严重降低性能。

要查看是否启用了透明的hugepages，运行以下命令并检查输出
```
cat defrag_file_pathname
cat enabled_file_pathname
```

- [always] never意味着启用了透明的hugepages
- always [never]意味着禁用透明的hugepages

要禁用透明的Hugepages，请在所有集群主机上执行如下

1、要在重新启动时禁用透明的hugepages, 将以下命令添加到`/etc/rc.d/rc.local`文件中所有集群主机上

```
if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
 echo never > /sys/kernel/mm/transparent_hugepage/enabled
fi

if test -f /sys/kernel/mm/transparent_hugepage/defrag; then
 echo never > /sys/kernel/mm/transparent_hugepage/defrag
fi
# for centos6
# echo never > /sys/kernel/mm/redhat_transparent_hugepage/defrag
# echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled
```
修改rc.local的文件权限
```
chmod +x /etc/rc.d/rc.local
```

2、修改GRUB配置以禁用THP（RHEL/CentOS 7）
将以下行添加到/etc/default/grub文件中的GRUB_CMDLINE_LINUX选项
```
transparent_hugepage=never
```
运行以下命令
```
grub2-mkconfig -o /boot/grub2/grub.cfg
```

#### 内核参数
将下列参数添加到/etc/sysctl.conf以优化各种网络行为
```
# 禁用TCP时间戳以提高CPU利用率(这是一个可选参数，将取决于您的NIC供应商):
net.ipv4.tcp_timestamps=0
# 启用TCP sack来提高吞吐量
net.ipv4.tcp_sack=1
# 增加处理器输入队列的最大长度
net.core.netdev_max_backlog=250000
# 使用setsockopt()增加TCP最大和默认缓冲区大小
net.core.rmem_max=4194304  # （以字节为单位）
net.core.wmem_max=4194304 
net.core.rmem_default=4194304 
net.core_wmem_default=4194304 
net.core.optmem_max=4194304
# 增加内存阈值以防止丢包
net.ipv4.tcp_rmem="4096 87380 4194304" 
net.ipv4.tcp_wmem="4096 65536 4194304"
# 为TCP启用低延迟模式
net.ipv4.tcp_low_latency=1
# 设置套接字缓冲区在TCP窗口大小和应用程序缓冲区之间均匀分配
net.ipv4.tcp_adv_win_scale=1


kernel.msgmnb = 65536
```

#### 选择最佳文件系统
在Linux中，有几种格式化和组织驱动器的选择。也就是说，只有少数选择是Hadoop的最佳选择

在RHEL/CentOS中，逻辑卷管理器(LVM)不应该用于数据驱动器。它不是最优的，并可能导致将多个驱动器组合到一个逻辑磁盘中，这与Hadoop跨HDFS管理容错的方式完全相反。在操作系统驱动器上保持启用LVM是有益的。系统可管理性的改进可以抵消可能出现的任何性能影响。在操作系统驱动器上使用LVM使管理员能够避免在分区上过度分配空间。空间需求可能会随时间变化，动态增长文件系统的能力比重新构建系统要好。不要使用LVM对逻辑卷进行条带或跨多个物理卷来模拟RAID

建议使用基于区段的文件系统。这包括ext3、ext4和xfs。大多数新的Hadoop集群默认使用ext4文件系统。Red Hat Enterprise Linux 7使用xfs作为其默认文件系统


在创建用于Hadoop数据卷的ext4文件系统时，我们建议将超级用户块保留从5%减少到1%(使用-m1选项)，并设置以下选项
```	
	每1 MB使用一个inode(大文件)
	最小化超级块备份的数量(sparse_super)
	启用日志记录(has_journal)
	为目录树使用b-tree索引(dir_index)
	使用基于区段的分配(extent)
```
```
# 创建这样一个ext4文件系统可能看起来像这样
mkfs –t ext4 –m 1 –O -T largefile \ 
sparse_super,dir_index,extent,has_journal /dev/sdb1 

# 创建一个xfs文件系统可能看起来像这样: 
mkfs –t xfs /dev/sdb1
# 在创建xfs文件系统时，不需要特殊的选项
```
磁盘挂载选项

HDFS本质上是一个容错文件系统。因此，DataNode机器用于数据的所有驱动器都需要在不使用RAID的情况下挂载。此外，应该使用noatime选项将驱动器挂载到/etc/fstab中(这也意味着nodiratime)。如果是SSD或flash，也可以通过在安装时指定discard选项来打开TRIM
```
# 在/etc/fstab中，确保适当的文件系统指定了noatime挂载选项:
/dev/sda1 / ext4 noatime 0 0

# 为了启用修剪(TRIM)，编辑/etc/fstab并设置挂载选项丢弃。
/dev/sdb1 /data ext4 noatime,discard 0 0
```


减少保留空间

默认情况下，ext3和ext4文件系统为根用户保留5%的空间。这个保留的空间算作使用的非DFS。要查看保留的空间，请使用tune2fs命令
```
# tune2fs -l /dev/sde1 | egrep "Block size:|Reserved block count"
Reserved block count:  36628312
Block size:            4096
```
保留的块数是保留的ext3/ext4文件系统块的数量。块大小是以字节为单位的大小。在本例中，在这个文件系统上保留了150 GB (139.72 GB)。

建议将DataNode卷的根用户块预留从5%减少到1%。使用tune2fs命令将预留空间设置为1%:
```
# tune2fs -m 1 /dev/sde1
```
