Elasticsearch提供了良好的默认设置，只需要很少的配置。在运行的集群上，可以使用集群更新设置API更改大多数设置。

Elasticsearch有三个配置文件

-  `elasticsearch.yml` 配置Elasticsearch
-  `jvm.options`  用于配置Elasticsearch JVM设置
-  `log4j2.properties` 配置Elasticsearch日志（docker下输出为console）

配置格式为YAML。

**path.data 和path.logs**   指定数据目录和日志目录，docker下默认为`/usr/share/elasticsearch/data,logs`

**cluster.name**   配置群集名称 集群中所有节点配置相同 如`-cluster.name=es-docker-cluster`

**node.name**  默认情况下，Elasticsearch将使用随机生成的UUID的前7个字符作为节点id。注意，节点id是持久化的，在节点重新启动时不会改变，因此默认节点名也不会改变

```
node.name: ${HOSTNAME}   或者 node.name: prod-data-2
# docker 下 -e node.name=es01
```

**network.host**  默认情况下，Elasticsearch只绑定回圈地址——例如。127.0.0.1(::1)。这足以在服务器上运行单个开发节点。为了与其他服务器上的节点形成集群，您的节点需要绑定到一个非环回地址。虽然有许多网络设置，通常你需要配置的全部是网络

```
network.host: 192.168.1.10
network.host: Hadoop1
network.host: 0.0.0.0
```

在投入生产之前，应该配置两个重要的发现和集群形成设置，以便集群中的节点可以互相发现并选择一个主节点

**discovery.seed_hosts**   主机发现 默认`127.0.0.1, [::1]`如果要在其他主机上形成包含节点的群集，则必须使用discovery.seed_hosts设置提供群集中其他节点的列表，这些节点符合主要条件且可能是实时且可联系的。即配置该节点会与哪些候选地址进行通信，hostname,ip ,ip+port （其中port默认设置`transport.profiles.default.port`如果没有设置端口,则为返回`transport.port`）

这个设置以前被称为`discovery.zen.ping.unicast.hosts `它的旧名称已被弃用，但为了保持向后兼容性，它继续工作。对旧名称的支持将在将来的版本中删除。

ES7移除 minimum_master_nodes 参数，让 Elasticsearch 自己选择可以形成仲裁的节点

```
-e discovery.seed_hosts=es01,es02
```

**cluster.initial_master_nodes**

当您第一次启动一个全新的Elasticsearch集群时，会有一个集群引导步骤，它确定一组符合主条件的节点，这些节点的选票在第一次选举中被统计。在开发模式中，没有配置发现设置，这个步骤由节点自己自动执行。由于这种自动引导在本质上是不安全的，所以当您在生产模式下启动一个全新的集群时，必须显式地列出符合主资格的节点，这些节点的选票应该在第一次选举中被统计。在重新启动集群或向现有集群添加新节点时，不应该使用此设置。

请确保集群中的值`cluster.initial_master_nodes`与node.name完全匹配

**discovery.type**

指定Elasticsearch是否应该形成一个多节点集群。默认情况下，Elasticsearch在形成集群时发现其他节点，并允许其他节点稍后加入集群。如果发现。当“type”设置为“single-node”时，Elasticsearch将形成单节点集群

**HTTP**

http模块允许通过http公开Elasticsearch api。可以为HTTP配置下表中的设置。它们都不是动态更新的，所以要使它们生效，应该在Elasticsearch配置文件中设置它们。

- `http.port`  绑定端口范围。默认为9200 - 9300

- `http.publish_port` HTTP客户端在与该节点通信时应该使用的端口。当集群节点位于代理或防火墙和http之后时非常有用。端口不能从外部直接寻址。默认值为通过http.port分配的实际端口

- `http.bind_host` 要绑定HTTP服务的主机地址。默认为`http.host`如果设置了)或`network.bind_host`

- `http.publish_host` 要发布供HTTP客户端连接的主机地址。默认为`http.host`(如果设置了)或`network.publish_host`

- `http.host`  用于设置`http.bind_host` 和 `http.publish_host`

- `http.max_content_length` HTTP请求的最大内容。默认为100 mb

- `http.max_initial_line_length` HTTP URL的最大长度。默认为4 kb

- `http.max_header_size` 允许的最大头文件大小。默认为8 kb

- `http.compression`  尽可能支持压缩(使用Accept-Encoding)。默认值为true。

- `http.compression_level` 定义用于HTTP响应的压缩级别。有效值范围为1(最小压缩)和9(最大压缩)。默认为3

- `http.cors.enabled` 启用或禁用跨源资源共享，例如，在另一个源上的浏览器是否可以执行针对Elasticsearch的请求。设置为true启用Elasticsearch来处理跨域请求  设置为false(默认值)使Elasticsearch忽略Origin请求头

- `http.cors.allow-origin`   允许跨域源。默认为不允许。如果你在值前添加/，它将被视为一个正则表达式。*表示允许所有

- `http.cors.max-age` Max-age定义了结果应该被缓存多长时间。默认为1728000(20天)

- `http.cors.allow-methods`  允许哪些方法。默认选项，`HEAD, GET, POST, PUT, DELETE。`

- `http.cors.allow-credentials` 是否应该返回Access-Control-Allow-Credentials头。注意:这个头信息只在设置为true时返回。默认值false


**Node**

```
node.master: true    
node.voting_only: false 
node.data: true 
node.ingest: true 
node.ml: true 
xpack.ml.enabled: true 
cluster.remote.connect: true 
```

**索引配置**

Elasticsearch 索引的配置项主要分为静态配置属性和动态配置属性，静态配置属性是索引创建后不能修改，而动态配置属性则可以随时修改。

- 静态配置：在创建索引或者关闭索引时创建

  - `index.number_of_shards`   # 索引的主分片数，默认值是 1。这个配置在索引创建后不能修改 。每个索引最多支持1024个分片。这个限制是一个安全限制，用于防止由于资源分配而意外创建索引而导致集群不稳定。可以通过在集群的每个节点上的系统属性指定`export ES_JAVA_OPTS="-Des.index.max_number_of_shards=128"`来修改这个限制

  - `index.shard.check_on_startup`:  # 在打开之前是否应该检查碎片是否存在腐败。当检测到腐败时，它将阻止碎片被打开
        false （default） 打开碎片时不要检查是否有腐败。
        checksum   检查物理腐败。
        true  检查物理和逻辑损坏。就CPU和内存使用而言，这要昂贵得多   代价高
        fix   检查物理和逻辑损坏。被报告损坏的片段将被自动删除。这个选项可能导致数据丢失。使用极端谨慎
    
  - `index.codec`:  默认值使用LZ4压缩压缩来压缩存储的数据 。但是可以将其设置为best_compression，它使用紧缩来获得更高的压缩比，以牺牲较慢的存储字段性能为代价。如果您正在更新压缩类型，那么将在合并段之后应用新的压缩类型。段合并可以强制使用force merge.

  - `index.routing_partition_size`: 自定义路由值可转到的碎片数目。默认值为1，只能在创建索引时设置,该值必须小于index.number_of_shards除非index.number_of_shards的值也是1

  - **index.analysis**

    分析器最外层的配置项，内部主要分为 char_filter、tokenizer、filter 和 analyzer。

    - **char_filter**：定义新的字符过滤器件。

    - **tokenizer**：定义新的分词器。

    - **filter**：定义新的 token filter，如同义词 filter。

    - **analyzer**：配置新的分析器，一般是 char_filter、tokenizer 和一些 token filter 的组合

- 动态配置：可以使用update-index-settings API在活动索引上更改它们

  - `index.number_of_replicas`: # 每个主碎片的副本数量。默认为1
  
  - `index.auto_expand_replicas`: # 根据集群中数据节点的数量自动扩展副本的数量  默认false 禁用
  
  - `index.refresh_interval`  # 执行新索引数据的刷新操作频率，该操作使对索引的最新更改对搜索可见，默认为 1s。也可以设置为 -1 以禁用刷新
  
  - `index.max_script_fields`  # 在查询中允许的script_fields的最大数量。默认为32
  
  - `index.max_refresh_listeners`索引的每个碎片上可用的刷新监听器的最大数量。这些监听器用于实现refresh=wait_for。
  
  - `index.blocks.read_only`  # 设置为true以使索引和索引元数据只读，设置为false以允许写入和元数据更改 
  
  - `index.blocks.read_only_allow_delete`  类似`read_only`但也允许删除索引以释放更多资源
  
  - `index.blocks.read` 设置为true将禁用对索引的读操作
  
  - `index.blocks.write`设置为true以禁用针对索引的数据写操作。与read_only'不同，此设置不影响元数据。例如，可以使用' write块关闭索引，但不能使用read_only块关闭索引
  
  - `index.blocks.metadata` 设置为true以禁用索引元数据的读写
  
    
  
  - `index.routing.allocation.enable` #控制该索引的碎片分配 默认all
  
    - all (default) - Allows shard allocation for all shards.
    - primaries - Allows shard allocation only for primary shards.
    - new_primaries - Allows shard allocation only for newly-created primary shards.
    - none - No shard allocation is allowed.
  
  - `index.routing.rebalance.enable`  # 为该索引实现碎片再平衡。默认all
    
    - all (default) - Allows shard rebalancing for all shards.
    - primaries - Allows shard rebalancing only for primary shards.
    - replicas - Allows shard rebalancing only for replica shards.
  - none - No shard rebalancing is allowed.
    
  - `index.routing.allocation.total_shards_per_node` 分配给单个节点的单个索引最大分片(副本和主分片)数量。默认为无限
  
  - `index.gc_deletes`已删除文档的版本号仍可用于将来版本化操作的时长。默认60s
  
- 其它配置

  - `index.mapping.coerce: false`  在所有映射类型中全局禁用强制转换
  - `node.store.allow_mmap: false`禁用使用内存映射的能力 默认true
  - `action.auto_create_index: false`   #  禁止自动创建索引



**bootstrap.memory_lock**

设置`bootstrap.memory_lock=true` JVM会在启动时锁定堆的初始大小，将进程地址空间锁定到RAM中 防止任何弹搜索内存被交换出去

**设置 heap size**

默认情况下，Elasticsearch告诉JVM使用最小和最大大小为1 GB的堆。当转移到生产环境时，重要的是配置堆大小，以确保Elasticsearch有足够的堆可用

- 将Xms和Xmx 大小设置相等
- 将Xmx设置为不超过物理RAM的50%
- 不要将Xmx设置为高于JVM用于压缩对象指针 26Gb 是安全的，但在某些系统上可能大到30 GB。 不要超过32Gb

通过变量 ES_JAVA_OPTS 来设置  `ES_JAVA_OPTS="-Xms4000m -Xmx4000m"`

**JVM heap dump path **

通过rpm 安装是在/var/lib/elasticsearch    docker下通过环境变量`ES_TMPDIR` 指定

**GC logging**

默认情况下，Elasticsearch支持GC日志。这些是在jvm中配置的。选项和默认的默认位置与Elasticsearch日志相同。默认配置每64 MB旋转一次日志，最多可以消耗2 GB的磁盘空间


