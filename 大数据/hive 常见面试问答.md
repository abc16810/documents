#### 请谈一下Hive的特点

hive是基于Hadoop的一个数据仓库工具，可以将结构化的数据文件映射为一张数据库表，并提供完整的sql查询功能，可以将sql语句转换为MapReduce任务进行运行。其优点是学习成本低，可以通过类SQL语句快速实现简单的MapReduce统计，不必开发专门的MapReduce应用，十分适合数据仓库的统计分析，但是Hive不支持实时查询。



#### hive 内部表和外部表的区别

- 建表时带有external关键字为外部表，否则为内部表
- 内部表和外部表建表时都可以自己指定location
- 删除表时，外部表不会删除对应的数据，只会删除元数据信息，内部表则会删除
- 其他用法是一样的

#### hive几种排序方式的区别

- **order by** 是要对输出的结果进行全局排序，这会导致所有map端数据都进入一个reducer中（多个reducer无法保证全局有序）在数据量大时可能会长时间计算不完，效率就很低。如果在严格模式下（hive.mapred.mode=strict）,则必须配合limit使用
- **sort by** 不是全局排序，只是在进入到reducer之前完成排序，只保证了每个reducer中数据按照指定字段的有序性，是局部排序。为了控制map端数据分配到reducer的key，往往还要配合 distribute by 一同使用。如果不加 distribute by 的话，map端数据就会随机分配到 reducer
- **distribute by** 指的是按照指定的字段划分到不同的输出reduce文件中，和sort by一起使用时需要注意，
  distribute by必须放在前面
- **group by** 作表示按照某些字段的值进行分组，有相同的值放到一起，一般和聚合函数一块用例如`AVG()，COUNT()，max(), main()`等一块用。
- **cluster by** 可以看做是一个特殊的distribute by+sort by，它具备二者的功能，但是只能实现倒序排序的方式,不能指定排序规则为asc 或者desc

#### hive的metastore的三种模式

- **内嵌Derby方式**

  这个是Hive默认的启动模式，一般用于单元测试，这种存储方式有一个缺点：在同一时间只能有一个进程连接使用数据库。

- **Local方式**

  本地MySQL

- **Remote方式**

  远程MySQL,一般常用此种方式

#### hive中join都有哪些

Hive中除了支持和传统数据库中一样的内关联（JOIN）、左关联（LEFT JOIN）、右关联（RIGHT JOIN）、全关联（FULL JOIN），还支持左半关联（LEFT SEMI JOIN）

- **内关联（JOIN）**只返回能关联上的结果。
- **左外关联（LEFT [OUTER] JOIN）**以LEFT [OUTER] JOIN关键字前面的表作为主表，和其他表进行关联，返回记录和主表的记录数一致，关联不上的字段置为NULL。
- **右外关联（RIGHT [OUTER] JOIN）**和左外关联相反，以RIGTH [OUTER] JOIN关键词后面的表作为主表，和前面的表做关联，返回记录数和主表一致，关联不上的字段为NULL。
- **全外关联（FULL [OUTER] JOIN）**以两个表的记录为基准，返回两个表的记录去重之和，关联不上的字段为NULL。
- **LEFT SEMI JOIN**以LEFT SEMI JOIN关键字前面的表为主表，返回主表的KEY也在副表中的记录
- **笛卡尔积关联（CROSS JOIN）**返回两个表的笛卡尔积结果，不需要指定关联键。



#### Impala 和 hive 的查询有哪些区别

**Impala是基于Hive的大数据实时分析查询引擎**，直接使用Hive的元数据库Metadata,意味着impala元数据都存储在Hive的metastore中。并且impala兼容Hive的sql解析，实现了Hive的SQL语义的子集，功能还在不断的完善中。

**Impala相对于Hive所使用的优化技术**

- 1、没有使用  MapReduce进行并行计算，虽然MapReduce是非常好的并行计算框架，但它更多的面向批处理模式，而不是面向交互式的SQL执行。与  MapReduce相比：Impala把整个查询分成一执行计划树，而不是一连串的MapReduce任务，在分发执行计划后，Impala使用拉式获取   数据的方式获取结果，把结果数据组成按执行树流式传递汇集，减少的了把中间结果写入磁盘的步骤，再从磁盘读取数据的开销。Impala使用服务的方式避免  每次执行查询都需要启动的开销，即相比Hive没了MapReduce启动时间。
- 2、使用LLVM产生运行代码，针对特定查询生成特定代码，同时使用Inline的方式减少函数调用的开销，加快执行效率。
- 3、充分利用可用的硬件指令（SSE4.2）。
- 4、更好的IO调度，Impala知道数据块所在的磁盘位置能够更好的利用多磁盘的优势，同时Impala支持直接数据块读取和本地代码计算checksum。
- 5、通过选择合适的数据存储格式可以得到最好的性能（Impala支持多种存储格式）。
- 6、最大使用内存，中间结果不写磁盘，及时通过网络以stream的方式传递。

#### Hive UDF简单介绍

在Hive中，用户可以自定义一些函数，用于扩展HiveQL的功能，而这类函数叫做UDF（用户自定义函数）。UDF分为两大类：UDAF（用户自定义聚合函数）和UDTF（用户自定义表生成函数）。

#### Hive底层与数据库交互原理

Hive 的查询功能是由 HDFS 和 
MapReduce结合起来实现的，对于大规模数据查询还是不建议在 hive 中，因为过大数据量会造成查询十分缓慢。Hive 与 
MySQL的关系：只是借用 MySQL来存储 hive 中的表的元数据信息，称为 metastore（元数据信息）

#### 对Hive桶表的理解？

桶表是对数据某个字段进行哈希取值，然后放到不同文件中存储。

数据加载到桶表时，会对字段取hash值，然后与桶的数量取模。把数据放到对应的文件中。物理上，每个桶就是表(或分区）目录里的一个文件，一个作业产生的桶(输出文件)和reduce任务个数相同。

桶表专门用于抽样查询，是很专业性的，不是日常用来存储数据的表，需要抽样查询时，才创建和使用桶表。

#### **数据倾斜怎么解决**

- 空值引发的数据倾斜： 1、可以直接不让null值参与join操作，即不让null值有shuffle阶段2，因为null值参与shuffle时的hash结果是一样的，那么我们可以给null值随机赋值，这样它们的hash结果就不一样，就会进到不同的reduce中：

- 不同数据类型引发的数据倾斜： 如果key字段既有string类型也有int类型，默认的hash就都会按int类型来分配，那我们直接把int类型都转为string就好了，这样key字段都为string，hash时就按照string类型分配了

  

#### 运维如何对hive进行调度

将hive的sql定义在脚本当中；使用azkaban或者oozie进行任务的调度；监控任务调度页面。



[参考](https://mp.weixin.qq.com/s?__biz=MzU3MzgwNTU2Mg==&mid=2247502750&idx=1&sn=bd9a9173d060dc4e4ebd49c8efc6acfe&chksm=fd3e8d0bca49041dea84da93910e5efdc4935e520525c09887c986691377aeb48e5cf7fb5667&scene=21#wechat_redirect)

