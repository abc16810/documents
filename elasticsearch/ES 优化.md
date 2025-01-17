### 集群架构优化

合理的部署 Elasticsearch 集群有助于提高服务的整体可用性

#### 主节点、数据节点和协调节点分离

Elasticsearch 集群在架构拓朴时，采用主节点、数据节点和负载均衡节点分离的架构，在 5.x 版本以后，又可将数据节点再细分为“Hot-Warm”的架构模式

详情请参照节点配置

#### 一台服务器上最好只部署一个 node

一台物理服务器上可以启动多个 node 服务器节点（通过设置不同的启动 port），但一台服务器上的 CPU、内存、硬盘等资源毕竟有限，从服务器性能考虑，不建议一台服务器上启动多个 node 节点

#### 集群分片设置

ES 一旦创建好索引后，就无法调整分片的设置，而在 ES 中，一个分片实际上对应一个 lucene 索引，而 lucene 索引的读写会占用很多的系统资源，因此，分片数不能设置过大；所以，在创建索引时，合理配置分片数是非常重要的。一般来说，我们遵循一些原则：

1. 控制每个分片占用的硬盘容量不超过 ES 的最大 JVM 的堆空间设置（一般设置不超过 32 G，参考上面的 JVM 内存设置原则），因此，如果索引的总容量在 500 G 左右，那分片大小在 16 个左右即可；当然，最好同时考虑原则 2。
2. 考虑一下 node 数量，一般一个节点有时候就是一台物理机，如果分片数过多，大大超过了节点数，很可能会导致一个节点上存在多个分片，一旦该节点故障，即使保持了 1 个以上的副本，同样有可能会导致数据丢失，集群无法恢复。所以，**一般都设置分片数不超过节点数的 3 倍**。

### 索引优化

#### 批量提交

当有大量数据提交的时候，建议采用批量提交（Bulk 操作）；此外使用 bulk 请求时，每个请求不超过几十 M，因为太大会导致内存使用过大。

比如在做 ELK 过程中，Logstash indexer 提交数据到 Elasticsearch 中，batch size 就可以作为一个优化功能点。但是优化 size 大小需要根据文档大小和服务器性能而定

#### 增加 Refresh 时间间隔

为了提高索引性能，Elasticsearch 在写入数据的时候，采用延迟写入的策略，即数据先写到内存中，当超过默认 1 秒（index.refresh_interval）会进行一次写入操作，就是将内存中 segment 数据刷新到磁盘中，此时我们才能将数据搜索出来，所以这就是为什么 Elasticsearch 提供的是近实时搜索功能，而不是实时搜索功能。

如果我们的系统对数据延迟要求不高的话，我们**可以通过延长 refresh 时间间隔，可以有效地减少 segment 合并压力，提高索引速度**。比如在做全链路跟踪的过程中，我们就将 `index.refresh_interval` 设置为 30s，减少 refresh 次数。再如，在进行导入索引时，可以将 refresh 次数临时关闭，即 `index.refresh_interval` 设置为-1及`index.number_of_replicas` 设置为 0，数据导入成功后再打开到正常模式及修改副本数，比如 30s，2

#### 修改 index_buffer_size 的设置

索引缓冲的设置可以控制多少内存分配给索引进程。这是一个全局配置，会应用于一个节点上所有不同的分片上。

```
indices.memory.index_buffer_size: 10%
indices.memory.min_index_buffer_size: 48mb
```

`indices.memory.index_buffer_size` 接受一个百分比或者一个表示字节大小的值。默认是 10%，意味着分配给节点的总内存的 10%用来做索引缓冲的大小。这个数值被分到不同的分片（shards）上。如果设置的是百分比，还可以设置 `min_index_buffer_size` （默认 48mb）和 `max_index_buffer_size`（默认没有上限）

#### 修改 translog 相关的设置

一是控制数据从内存到硬盘的操作频率，以减少硬盘 IO。这是一个昂贵的操作，可将 sync_interval 的时间设置大一些。默认为 5s

默认情况下，``index.translog.durability``为request，这意味着当translog在主节点和每个已分配的副本上成功fsync并提交后，Elasticsearch将只向客户端报告成功的索引、删除、更新或批量请求。如果``index.translog.durability``为async，那么Elasticsearch只对每个`index.translog.sync_interval`进行fsync和提交。这意味着在崩溃之前执行的任何操作都可能在节点恢复时丢失

```
index.translog.sync_interval: 5s  
index.translog.durability: request #  是否在每次索引、删除、更新或批量请求后进行fsync并提交translog,确保数据没有丢失
```

也可以控制 tranlog 数据块的大小，达到 threshold 大小时，才会 flush 到 lucene 索引文件。默认为 512m。

```
index.translog.flush_threshold_size: 512mb
```

#### 注意 _id 字段的使用

_id 字段的使用，应尽可能避免自定义 _id，以避免针对 ID 的版本管理；建议使用 ES 的默认 ID 生成策略或使用数字类型 ID 做为主键

####  _all 字段及 _source 字段的使用

**_**all 字段及 _source 字段的使用，应该注意场景和需要，_all 字段包含了所有的索引字段，方便做全文检索，如果无此需求，可以禁用；_source 存储了原始的 document 内容，如果没有获取原始文档数据的需求，可通过设置 includes、excludes 属性来定义放入 _source 的字段

#### 合理的配置使用 index 属性

合理的配置使用 index 属性，analyzed 和 not_analyzed，根据业务需求来控制字段是否分词或不分词。只有 groupby 需求的字段，配置时就设置成 not_analyzed，以提高查询或聚类的效率

#### 减少副本数量

Elasticsearch 默认副本数量为 3 个，虽然这样会提高集群的可用性，增加搜索的并发数，但是同时也会影响写入索引的效率。

在索引过程中，需要把更新的文档发到副本节点上，等副本节点生效后在进行返回结束。使用 Elasticsearch 做业务搜索的时候，建议副本数目还是设置为 3 个，但是像内部 ELK 日志系统、分布式跟踪系统中，完全可以将副本数目设置为 1 个

### 查询优化

#### 路由优化

当我们查询文档的时候，Elasticsearch 如何知道一个文档应该存放到哪个分片中呢？它其实是通过下面这个公式来计算出来的。

```
shard = hash(routing) % number_of_primary_shards
```

routing 默认值是文档的 id，也可以采用自定义值，比如用户 ID

**不带 routing 查询**

在查询的时候因为不知道要查询的数据具体在哪个分片上，所以整个过程分为 2 个步骤：

1. 分发：请求到达协调节点后，协调节点将查询请求分发到每个分片上。
2. 聚合：协调节点搜集到每个分片上查询结果，再将查询的结果进行排序，之后给用户返回结果。

**带 routing 查询**

查询的时候，可以直接根据 routing 信息定位到某个分配查询，不需要查询所有的分配，经过协调节点排序。

向上面自定义的用户查询，如果 routing 设置为 userid 的话，就可以直接查询出数据来，效率提升很多。

#### Filter VS Query

尽可能使用过滤器上下文（Filter）替代查询上下文（Query）

- Query：此文档与此查询子句的匹配程度如何？
- Filter：此文档和查询子句匹配吗？

Elasticsearch 针对 Filter 查询只需要回答「是」或者「否」，不需要像 Query 查询一样计算相关性分数，同时 Filter 结果可以缓存

#### 深度翻页

在使用 Elasticsearch 过程中，应尽量避免大翻页的出现。

正常翻页查询都是从 from 开始 size 条数据，这样就需要在每个分片中查询打分排名在前面的 from+size 条数据。协同节点收集每个分配的前 from+size 条数据。协同节点一共会受到 N*(from+size) 条数据，然后进行排序，再将其中 from 到 from+size 条数据返回出去。如果 from 或者 size 很大的话，导致参加排序的数量会同步扩大很多，最终会导致 CPU 资源消耗增大。

可以通过使用 Elasticsearch scroll 和 scroll-scan 高效滚动的方式来解决这样的问题。

也可以结合实际业务特点，文档 id 大小如果和文档创建时间是一致有序的，可以以文档 id 作为分页的偏移量，并将其作为分页查询的一个条件

### 数据结构优化

#### 尽量减少不需要的字段

如果 Elasticsearch 用于业务搜索服务，一些不需要用于搜索的字段最好不存到 ES 中，这样即节省空间，同时在相同的数据量下，也能提高搜索性能。

避免使用动态值作字段，动态递增的 mapping，会导致集群崩溃；同样，也需要控制字段的数量，业务中不使用的字段，就不要索引。控制索引的字段数量、mapping 深度、索引字段的类型，对于 ES 的性能优化是重中之重

#### Nested Object vs Parent/Child

尽量避免使用 nested 或 parent/child 的字段，能不用就不用；nested query 慢，parent/child query 更慢，比 nested query 慢上百倍；因此能在 mapping 设计阶段搞定的（大宽表设计或采用比较 smart 的数据结构），就不要用父子关系的 mapping

如果一定要使用 nested fields，保证 nested fields 字段不能过多，目前 ES 默认限制是 50。因为针对 1 个 document，每一个 nested field，都会生成一个独立的 document，这将使 doc 数量剧增，影响查询效率，尤其是 JOIN 的效率

| 对比 | Nested Object                        | Parent/Child                                       |
| ---- | ------------------------------------ | -------------------------------------------------- |
| 优点 | 文档存储在一起，因此读取性高         | 父子文档可以独立更新，互不影响                     |
| 缺点 | 更新父文档或子文档时需要更新整个文档 | 为了维护 join 关系，需要占用部分内存，读取性能较差 |
| 场景 | 子文档偶尔更新，查询频繁             | 子文档更新频繁                                     |

#### 选择静态映射，非必需时，禁止动态映射

尽量避免使用动态映射，这样有可能会导致集群崩溃，此外，动态映射有可能会带来不可控制的数据类型，进而有可能导致在查询端出现相关异常，影响业务。

此外，Elasticsearch 作为搜索引擎时，主要承载 query 的匹配和排序的功能，那数据的存储类型基于这两种功能的用途分为两类，一是需要匹配的字段，用来建立倒排索引对 query 匹配用，另一类字段是用做粗排用到的特征字段，如 ctr、点击数、评论数等等

### 其它

#### head请求跨域问题

```
http.cors.enabled: true
http.cors.allow-origin: /https?://10.4.55.209(:[0-9]+)?/
```

#### keyword类型字节限制

如果一个字段的类型是 `keyword`，而实际写入数据时指定了一个非常长的文本值，会报错：`illegal_argument_exception`、`max_bytes_length_exceeded_exception`，导致整个文档写入失败并返回异常

对于这种超长文本写入到一个 `keyword` 类型的字段中，对于 `Elasticsearch` 是不友好的，底层的 `Lucene` 也无法支持。

解决方法： 

- 类型定义为分析类型，即 `text`，并指定必要的分析器。
- 对写入的数据提前判断截取
- 通过`ignore_above` 指定值，超过`ignore_above` 设置的字符串将不会被索引或存储

`ignore_above` 参数限制的是字符数，具体字节数要根据实际内容转换，如果内容中都是字母、数字，则字符数就是字节数，如果您使用带有许多非ascii字符的UTF-8文本，您可能希望将限制设置为32766 / 4 = 8191，因为UTF-8字符可能最多占用4个字节

通过聚合或者`term`匹配时查不到数据超过`ignore_above`设置的字符数的文档， 说明 `Elasticsearch` 在写入该字段的值时没有对超过`ignore_above`的值做索引，只是简单的存储，也就无法查询。

字段的 `ignore_above` 可以更新，类型不会变更，不会影响已经存储的内容，只会影响以后写入的内容，因为字段类型并没有变化，只是限制了写入长度。





