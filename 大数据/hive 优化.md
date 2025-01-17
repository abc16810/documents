#### 执行引擎

Hive支持多种执行引擎，分别是 MapReduce、Tez、Spark、Flink

```
hive.execution.engine=spark  # mr tez spark flink
# Tez是一个构建于YARN之上的支持复杂的DAG(有向无环图)任务的数据处理框架,执行速度大于mr
```

#### 文件格式

Hive表支持的存储格式有TextFile、SequenceFile、RCFile、ORC、Parquet等。存储格式一般需要根据业务进行选择，生产环境中绝大多数表都采用TextFile、 ORC、Parquet存储格式之一。

TextFile是最简单的存储格式，它是纯文本记录，也是Hive的默认格式。其磁盘开销大，查询效率低，更多的是作为跳板来使用。RCFile、ORC、Parquet等格式的表都不能由文件直接导入数据，必须由TextFile来做中转

Parquet和ORC都是Apache旗下的开源列式存储格式。列式存储比起传统的行式存储更适合批量OLAP查询，并且也支持更好的压缩和编码。选择Parquet的原因主要是它支持Impala查询引擎，并且对update、delete和事务性操作需求很低

如果要以减少存储空间并提高性能的优化方式存储数据，则可以使用**ORC文件**格式

如果数据存储在小于块大小的小文件中，则可以使用**SEQUENCE**文件格式

而当列中嵌套的数据过多时，**Parquet**格式会很有用

#### CBO(成本优化器)

Hive有两种优化器：Vectorize(向量化优化器) 与 Cost-Based Optimization (CBO成本优化器)

Hive的基于成本的优化器(CBO)是Hive查询处理引擎的核心组件。CBO由Apache Calcite提供支持，它对查询的各种计划的成本进行优化和计算。

CBO的主要目标是通过检查查询中指定的表和条件来生成有效的执行计划，最终减少查询执行时间并降低资源利用率。解析之后，查询被转换成逻辑树(抽象语法树)，该树表示查询必须执行的操作，比如读取特定的表或执行内部连接

```
hive.cbo.enable=true
hive.stats.autogather=true
```

#### statistics （统计）

收集列和表的统计信息，以获得最佳的查询性能。

必须计算列和表统计信息以获得最优的Hive性能，因为它们对于估计谓词选择性和计划成本至关重要。在没有表统计信息的情况下，Hive CBO不工作。某些高级重写需要列统计信息。

确保将下表中的配置属性设置为true，以改进生成统计信息的查询的性能。可以使用`Ambari/CDH`设置属性，也可以定制hive-site.xml文件

```
hive.stats.fetch.column.stats=true
hive.compute.query.using.stats=true
```

**生成Hive Statistics**

ANALYZE TABLE命令生成表和列的统计信息。下面几行显示了如何在Hive对象上生成不同类型的统计信息。

- 收集非分区表的表统计信息

  ```
  ANALYZE TABLE [table_name] COMPUTE STATISTICS;
  ```

- 收集分区表的表统计信息

  ```
  ANALYZE TABLE [table_name] PARTITION(partition_column) COMPUTE STATISTICS;
  ```

- 收集整个表的列统计信息

  ```
  ANALYZE TABLE [table_name] COMPUTE STATISTICS for COLUMNS [comma_separated_column_list];
  ```

- 使用键x在col1上分区的表上收集partition2列的统计信息

  ```
  ANALYZE TABLE partition2 (col1="x") COMPUTE STATISTICS for COLUMNS;
  ```

使用description语句查看CBO生成的统计信息，使用description语句查看CBO生成的统计信息

#### 向量化

默认情况下，Hive查询执行引擎一次只处理表中的一行。在处理下一行之前，单行数据要经过查询中的所有操作符，这导致了非常低效的CPU使用。在向量化查询执行中，数据行被批处理在一起，并表示为一组列向量。向量化查询执行的基本思想是将一批行作为列向量的数组处理。当启用查询向量化时，查询引擎将处理列的向量，这将大大提高典型查询操作(如扫描、筛选、聚合和连接)的CPU利用率

CDH 6和CDH 5默认开启Hive查询向量功能。但是，在CDH 5中，Hive中的向量查询只能在orc格式的表上执行，为了与CDH平台的整体兼容性，Cloudera建议您不要使用orc格式的表。相反，Cloudera建议您使用Parquet格式的表格，因为所有的CDH组件都支持这种格式，并且所有的CDH组件都可以使用这种格式 

启用或禁用`Parquet`格式文件的Hive查询向量化

```
SET hive.vectorized.execution.enabled=true;
SET hive.vectorized.input.format.excludes= ;
# SET hive.vectorized.input.format.excludes=org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat;
```

 Hive查询向量化调优其它选项

```
hive.vectorized.adaptor.usage.mode = chosen
# 仅当执行引擎为Spark时有效
hive.vectorized.execution.reduce.enabled= true （默认）
hive.vectorized.groupby.checkinterval=4096 (默认100000)
# 这将设置存储在内存中的数据量。要提高性能，请增加设置。但是，要谨慎地增加设置，以防止内存不足问题，将刷新百分比设置为10%
hive.vectorized.groupby.flush.percent = 0.1
# 如果希望向量化查询和非向量化查询的结果一致，请将此属性设置为true
hive.vectorized.use.checked.expressions = true
hive.vectorized.use.vectorized.input.format = true
hive.vectorized.use.vector.serde.deserialize = false
```

 要验证查询是否被向量化，请使用EXPLAIN VECTORIZATION语句。该语句返回一个查询计划，显示Hive查询执行引擎如何处理您的查询，以及是否正在触发向量化

```
explain select count(*) from vectorizedtable; 
# explain输出信息 
STAGE PLANS: 
 Stage: Stage-1 
  Map Reduce 
   Alias -> Map Operator Tree: 
   ... 
   Execution mode: vectorized 
   ... 
 ...
```

#### 使用分区和存储桶设计数据存储

**分区**

在Hive中，表通常是分区的。分区映射到文件系统上的物理目录。通常，表是按日期时间分区的，因为传入的数据每天都被加载到Hive中。大型部署可以有成千上万个分区。

如果一个查询在分区列上有一个过滤器，那么使用分区可以显著提高性能，这样可以将分区扫描减少到一个或几个符合过滤条件的分区，所以执行速度会比较快。分区修剪是在WHERE子句中出现分区键时直接进行的。当在查询处理过程中发现分区键时，会间接地进行修剪。例如，在与维度表连接之后，分区键可能来自维度表。

分区字段的选择是影响查询性能的重要因素，尽量避免层级较深的分区，这样会造成太多的子文件夹。一些常见的分区字段可以是：

- 日期或时间。如year、month、day或者hour，当表中存在时间或者日期字段时
- 地理位置。如国家、省份、城市等
- 业务逻辑。如部门、销售区域、客户等等

**桶表**

与分区表类似，分桶表的组织方式是将HDFS上的文件分割成多个文件。

分桶可以加快数据采样，也可以提升join的性能(join的字段是分桶字段)，因为分桶可以确保某个key对应的数据在一个特定的桶内(文件)，巧妙地选择分桶字段可以大幅度提升join的性能。

通常情况下，分桶字段可以选择经常用在过滤操作或者join操作的字段



#### HiveServer2

以下是调整HiveServer2实例堆内存大小的一般建议：

- 1到20个并发执行查询: 设置为6gb堆大小.
- 1到40个并发执行查询：设置为12gb堆大小
- 超过40个并发执行查询:创建一个新的HiveServer2实例。

#### **本地模式**

对于大多数情况，Hive可以通过本地模式在单台机器上处理所有任务。

对于小数据，执行时间可以明显被缩短。通过`set hive.exec.mode.local.auto=true`（默认为false）设置本地模式

```
SET hive.exec.mode.local.auto=true; -- 默认 false
SET hive.exec.mode.local.auto.inputbytes.max=50000000; 
SET hive.exec.mode.local.auto.input.files.max=5; -- 默认 4
# 输入的文件大小小于50000000，map任务数小于5，reduce任务的数量是1或者0 才启用本地模式
```

#### **严格模式**

使用严格模式可以禁止以下三种类型的查询`set hive.mapred.mode=strict `

- 查询分区表时不限定分区列的语句
- 两表join产生了笛卡尔积的语句
- 用order by来排序，但没有指定limit的语句

#### 并行执行

Hive会将一个查询转化成一个或者多个阶段。这样的阶段可以是MapReduce阶段、抽样阶段、合并阶段、limit阶段。

默认情况下，Hive一次只会执行一个阶段，由于job包含多个阶段，而这些阶段并非完全互相依赖，

即：这些阶段可以并行执行，可以缩短整个job的执行时间。设置参数：`set hive.exec.parallel=true`,（默认false）或者通过配置文件来完成

```
hive.exec.parallel=true;
hive.exec.parallel.thread.number=16;
mapreduce.input.fileinputformat.split.minsize=256mb
# 并行执行可以增加集群资源的利用率
```

#### 动态分区

```
# 设置开启动态分区
SET hive.exec.dynamic.partition=true;   #开启动态分区，默认是false
SET hive.exec.dynamic.partition.mode=nonstrict   #开启允许所有分区都是动态的，否则必须要有静态分区才能使用

```

#### 其它配置

```
hive.optimize.reducededuplication.min.reducer=4  # 如果一个简单查询只包括一个group by和order by，此处可以设置为1或2
hive.optimize.reducededuplication=true  # 如果数据已经根据相同的key做好聚合，那么去除掉多余的map/reduce作业

hive.merge.mapfiles=true  # 设置map端输出进行合并，默认为true
hive.merge.mapredfiles=false  # 设置reduce端输出进行合并，默认为false
hive.merge.smallfiles.avgsize=16000000  # 当作业的平均输出文件大小小于此值时，Hive将启动一个附加的
map-reduce作业将输出文件合并到更大的文件中
hive.merge.size.per.task=256000000  # 作业结束时合并文件的大小
hive.merge.sparkfiles=true  # 在Spark DAG转换结束时合并小文件  默认false
hive.merge.tezfiles=true # 在Tez DAG的末尾合并小文件  默认false

hive.auto.convert.join=true   # Map Join优化, 不太大的表直接通过map过程做join
hive.auto.convert.join.noconditionaltask=true
hive.auto.convert.join.noconditionaltask.size=20M(might need to increase for Spark, 200M)

hive.optimize.bucketmapjoin=false   # 如果数据按照join的key分桶，hive将简单优化inner join(官方推荐关闭)
hive.optimize.bucketmapjoin.sortedmerge=false

hive.map.aggr=true   # map端聚合(跟group by有关), 如果开启, Hive将会在map端做第一级的聚合
hive.map.aggr.hash.percentmemory=0.5  # 所有map任务可以用作Hashtable的内存百分比, 如果OOM, 调小这个参数(官方默认0.5)

hive.optimize.sort.dynamic.partition=false  # hive0.13有个bug, 开启这个配置会对所有字段排序

hive.stats.autogather=true   # 新创建的表/分区是否自动计算统计数据
hive.stats.fetch.column.stats=true
hive.compute.query.using.stats=true
hive.stats.fetch.partition.stats=true

hive.limit.pushdown.memory.usage=0.04 (MR and Spark)  # 在order by limit查询中分配给存储Top K的内存为4% 

hive.optimize.index.filter=true  # 是否开启自动使用索引

hive.smbjoin.cache.rows=10000  # Map Join任务HashMap中key对应value数量

hive.fetch.task.conversion=more   # 将只有SELECT, FILTER, LIMIT转化为FETCH, 减少等待时间
hive.fetch.task.conversion.threshold=1073741824

hive.optimize.ppd=true   #默认true
```