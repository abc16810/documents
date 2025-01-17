#### Elasticsearch  简介

Elasticsearch  是一个分布式、RESTful 风格的搜索和数据分析引擎。

Elasticsearch  基于搜索库 Lucene 开发。ElasticSearch 隐藏了 Lucene 的复杂性，提供了简单易用的 REST API / Java API 接口（另外还有其他语言的 API 接口， 如python）。

ElasticSearch 可以视为一个文档存储，它将复杂数据结构序列化为 JSON 存储

ElasticSearch 是一个近实时搜索平台。从索引文档到可搜索文档有较小的延迟(通常是一秒)

#### Cluster

集群包含多个节点，每个节点属于哪个集群都是通过一个配置来决定的，对于中小型应用来说，一个节点就可以作为一个集群运行。

拥有相同 `cluster.name` 配置的 Elasticsearch 节点组成一个**集群**。 `cluster.name` 默认名为 `elasticsearch`，可以通过配置文件修改，或启动时通过 `-E cluster.name=xxx` 指定

当有节点加入集群中或者从集群中移除节点时，集群将会重新平均分布所有的数据

#### Node

节点是单个服务器，它是集群的一部分，存储数据，并参与集群的索引和搜索功能。与集群一样，节点的名称默认为在启动时分配给节点的随机惟一标识符(UUID)。如果不需要默认值，可以定义任何节点名称。这个名称对于管理非常重要，因为您想要确定网络中的哪些服务器对应于Elasticsearch集群中的哪些节点。

可以通过集群名称配置节点以加入特定的集群。默认情况下，每个节点都被设置为加入一个名为elasticsearch的集群，这意味着如果在网络上启动多个节点——假设它们可以相互发现——它们将自动形成并加入一个名为elasticsearch的集群

**Node类型**

- 主节点（master node）每个节点都保存了集群的状态，只有 master 节点才能修改集群的状态信息（保证数据一致性）。集群状态，维护了以下信息： 
  - 所有的节点信息
  - 所有的索引和其相关的 mapping 和 setting 信息
  - 分片的路由信息
- 候选节点（master eligible node）master eligible 节点可以参加选主流程。第一个启动的节点，会将自己选举为 mater 节点。 
  - 每个节点启动后，默认为 master eligible 节点，可以通过配置 `node.master: false` 禁止
- **数据节点（data node）**：负责保存分片数据。
- **协调节点（coordinating node）**：负责接收客户端的请求，将请求分发到合适的接地那，最终把结果汇集到一起。每个 Elasticsearch 节点默认都是协调节点（coordinating node）。
- **冷/热节点（warm/hot node）**：针对不同硬件配置的数据节点（data node），用来实现 Hot & Warm 架构，降低集群部署的成本。
- **机器学习节点（machine learning node）**：负责执行机器学习的 Job，用来做异常检测。

| 配置参数    | 默认值 | 说明                                  |
| ----------- | ------ | ------------------------------------- |
| node.master | true   | 是否为主节点                          |
| node.data   | true   | 是否为数据节点                        |
| node.ingest | true   |                                       |
| node.ml     | true   | 是否为机器学习节点（需要开启 x-pack） |

> 开发环境中一个节点可以承担多种角色。但是，在生产环境中，节点应该设置为单一角色

#### Index 索引

索引是具有类似特征的文档的集合（一个 **索引** 类似于传统关系数据库中的一个 **数据库**）。例如，您可以有一个客户数据索引、另一个产品目录索引和另一个订单数据索引。索引由一个名称标识(必须是小写的)，该名称用于在对其中的文档执行索引、搜索、更新和删除操作时引用索引。

#### Type 类型

一种类型过去是索引的逻辑类别/分区，允许您在同一索引中存储不同类型的文档，

一种类型的用户，另一种类型的博客帖子。在索引中创建多个类型不再可能，类型的整个概念将在稍后的版本中删除。有关更多信息，请参见删除映射类型。

See [*Removal of mapping types*](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/removal-of-types.html)

> Elastic 6.x 版只允许每个 Index 包含一个 Type，7.x 版将会彻底移除 Type

#### Document 文档

Index 里面单条的记录称为 Document（文档）。许多条 Document 构成了一个 Index。

每个 `文档（document）` 都是字段（field）的集合。

同一个 Index 里面的 Document，不要求有相同的结构（scheme），但是最好保持相同，这样有利于提高搜索效率

**文档的元数据**

一个文档不仅仅包含它的数据 ，也包含**元数据** —— 有关文档的信息。

- `_index`：文档在哪存放
- `_type`：文档表示的对象类别
- `_id`：文档唯一标识
- `_source`：文档的原始 Json 数据
- `_all`：整合所有字段内容到该字段，已被废除
- `_version`：文档的版本信息
- `_score`：相关性打分

#### Field

**字段（field）** 是包含数据的键值对。

默认情况下，Elasticsearch 对每个字段中的所有数据建立索引，并且每个索引字段都具有专用的优化数据结构。



#### Shards & Replicas（分片和副本）

索引可能存储大量数据，超出单个节点的硬件限制。例如，一个包含10亿个文档的索引占用了1TB的磁盘空间，它可能不适合于单个节点的磁盘，或者可能太慢，无法单独为单个节点提供搜索请求。

为了解决这个问题，Elasticsearch提供了将索引细分为多个碎片的功能。当您创建索引时，您可以简单地定义您想要的碎片的数量。每个碎片本身都是一个功能齐全、独立的“索引”，可以驻留在集群中的任何节点上

在创建索引时，每个索引可以定义碎片和副本的数量。创建索引之后，还可以随时动态更改副本的数量。您可以使用_shrink和_split api更改现有索引的碎片数量，但是这不是一项简单的任务，预先计划正确的碎片数量是最佳方法

默认情况下，Elasticsearch中的每个索引分配5个主碎片和1个副本，这意味着如果集群中至少有两个节点，那么索引将有5个主碎片和5个副本碎片(1个完整副本)，每个索引总共有10个碎片

Elasticsearch 是利用分片将数据分发到集群内各处的。分片是数据的容器，文档保存在分片内，分片又被分配到集群内的各个节点里。 当你的集群规模扩大或者缩小时， Elasticsearch 会自动的在各节点中迁移分片，使得数据仍然均匀分布在集群里

主分片：用于解决数据水平扩展的问题。通过主分片，可以将数据分布到集群内不同节点上。

- 索引内任意一个文档都归属于一个主分片。
- 主分片数在索引创建时指定，后序不允许修改，除非 Reindex

副分片（Replica Shard）：用于解决数据高可用的问题。副分片是主分片的拷贝。副本分片作为硬件故障时保护数据不丢失的冗余备份，并为搜索和返回文档等读操作提供服务。

- 副分片数可以动态调整
- 增加副本数，还可以在一定程度上提高服务的可用性（读取的吞吐）

 副本（Replicas）

副本主要是针对主分片（Shards）的复制，Elasticsearch 中主分片可以拥有 0 个或多个的副本。

副本分片的主要目的就是为了故障转移。

分片副本很重要，主要有两个原因：

- 它在分片或节点发生故障时提供高可用性。因此，副本分片永远不会在与其复制的主分片相同的节点；
- 副本分片也可以接受搜索的请求，可以并行搜索，从而提高系统的吞吐量。



#### ElasticSearch 基本原理

 **ES 写数据过程**

1. 客户端选择一个 node 发送请求过去，这个 node 就是 `coordinating node`（协调节点）。
2. coordinating node 对 document 进行**路由**，将请求转发给对应的 node（有 primary shard）。改 node处理请求，然后将数据同步到 `replica node`。
3. `coordinating node` 如果发现 `primary node` 和所有 `replica node` 都搞定之后，就返回响应结果给客户端



**ES 读数据过程**

可以通过 `doc id` 来查询，会根据 `doc id` 进行 hash，判断出来当时把 `doc id` 分配到了哪个 shard 上面去，从那个 shard 去查询

1. 客户端发送请求到**任意**一个 node，成为 `coordinate node`。
2. `coordinate node` 对 `doc id` 进行哈希路由，将请求转发到对应的 node，此时会使用 `round-robin` **轮询算法**，在 `primary shard` 以及其所有 replica 中随机选择一个，让读请求负载均衡。
3. 接收请求的 node 返回 document 给 `coordinate node`。
4. `coordinate node` 返回 document 给客户端



**es搜索数据过程**

1. 客户端发送请求到一个 `coordinate node`
2. 协调节点将搜索请求转发到**所有**的 shard 对应的 `primary shard` 或 `replica shard` ，都可以
3. query phase：每个 shard 将自己的搜索结果（其实就是一些 `doc id` ）返回给协调节点，由协调节点进行数据的合并、排序、分页等操作，产出最终结果
4. fetch phase：接着由协调节点根据 `doc id` 去各个节点上**拉取实际**的 `document` 数据，最终返回给客户端



**写数据底层原理**

数据先写入内存 buffer，然后每隔 1s，将数据 refresh 到 os cache，到了 os cache 数据就能被搜索到（所以我们才说 es 从写入到能被搜索到，中间有 1s 的延迟）。每隔 5s，将数据写入 translog 文件（这样如果机器宕机，内存数据全没，最多会有 5s 的数据丢失），translog 大到一定程度，或者默认每隔 30mins，会触发 commit 操作，将缓冲区的数据都 flush 到 segment file 磁盘文件中

> 数据写入 segment file (os cache)之后，同时就建立好了倒排索引



**删除/更新数据底层原理**

如果是删除操作，commit 的时候会生成一个 `.del` 文件，里面将某个 doc 标识为 `deleted` 状态，那么搜索的时候根据 `.del` 文件就知道这个 doc 是否被删除了

如果是更新操作，就是将原来的 doc 标识为 `deleted` 状态，然后新写入一条数据

buffer 每 refresh 一次，就会产生一个 `segment file`，所以默认情况下是 1 秒钟一个 `segment file`，这样下来 `segment file` 会越来越多，此时会定期执行 merge。每次 merge 的时候，会将多个 `segment file` 合并成一个，同时这里会将标识为 `deleted` 的 doc 给**物理删除掉**，然后将新的 `segment file` 写入磁盘，这里会写一个 `commit point`，标识所有新的 `segment file`，然后打开 `segment file` 供搜索使用，同时删除旧的 `segment file`。



**倒排索引**

在搜索引擎中，每个文档都有一个对应的文档 ID，文档内容被表示为一系列关键词的集合。例如，文档 1 经过分词，提取了 20 个关键词，每个关键词都会记录它在文档中出现的次数和出现位置。

那么，倒排索引就是**关键词到文档** ID 的映射，每个关键词都对应着一系列的文件，这些文件中都出现了关键词

有了倒排索引，搜索引擎可以很方便地响应用户的查询。比如用户输入查询 `Facebook`，搜索系统查找倒排索引，从中读出包含这个单词的文档，这些文档就是提供给用户的搜索结果。

- 倒排索引中的所有词项对应一个或多个文档；
- 倒排索引中的词项**根据字典顺序升序排列**

