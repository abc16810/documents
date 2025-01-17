

如果选出的主节点被其他任务负载，则集群可能无法正常运行。特别是，对数据进行索引和搜索可能会耗费大量资源，因此在大型或高吞吐量集群中，最好避免使用主节点执行索引和搜索等任务。可以通过将三个节点配置为专用的符合主资格的节点来实现这一点。专用的` master-eligible`只具有主角色，允许它们专注于管理集群。虽然主节点也可以作为协调节点，将客户端搜索和索引请求路由到数据节点，但最好不要使用专用的主节点来实现这个目的

若要在默认分布中创建一个专用的` master-eligible`，请设置

```
node.master: true     # 系统默认启用“角色
node.voting_only: false   # 默认false
node.data: false          # 数据节点 默认true
node.ingest: false       #  摄取默认true
node.ml: false              # 机器学习节点 默认true
xpack.ml.enabled: true                 # 默认true
cluster.remote.connect: false   # 禁用远程集群连接  默认true
```

数据节点

数据节点保存包含已建立索引的文档的分片。数据节点处理与数据相关的操作，如CRUD、搜索和聚合。这些操作都是I/O、内存和cpu密集型的。重要的是要监视这些资源，并在它们过载时添加更多的数据节点。

使用专用数据节点的主要好处是可以分离主角色和数据角色

```
node.master: false 
node.voting_only: false 
node.data: true 
node.ingest: false 
node.ml: false 
cluster.remote.connect: false 
```

在 Elasticsearch 5.x 版本之后，data 节点又可再细分为“Hot-Warm”架构，即分为热节点（hot node）和暖节点（warm node）

hot 节点：

hot 节点主要是索引节点（写节点），同时会保存近期的一些频繁被查询的索引。由于进行索引非常耗费 CPU 和 IO，即属于 IO 和 CPU 密集型操作，建议使用 SSD 的磁盘类型，保持良好的写性能；我们推荐部署最小化的 3 个 hot 节点来保证高可用性。根据近期需要收集以及查询的数据量，可以增加服务器数量来获得想要的性能

如果是针对指定的 index 操作，可以通过 settings 设置 `index.routing.allocation.require.box_type: hot` 将索引写入 hot 节点

```
node.attr.box_type: hot   # 热节点
node.attr.box_type: Warm  # 索引不再被更新，但仍然被查询
node.attr.box_type: cold  # 冷节点 索引不再被更新，也不经常被查询。这些信息仍然需要是可搜索的
delete  # 索引不再需要，可以安全地删除
```

warm 节点：

这种类型的节点是为了处理大量的，而且不经常访问的只读索引而设计的。由于这些索引是只读的，warm 节点倾向于挂载大量磁盘（普通磁盘）来替代 SSD。内存、CPU 的配置跟 hot 节点保持一致即可；节点数量一般也是大于等于 3 个



Ingest Node

摄取节点可以执行由一个或多个摄取处理器组成的预处理管道。根据摄取处理器执行的操作类型和所需资源的不同，使用专用的摄取节点可能是有意义的，这些节点将只执行这个特定的任务。

```
node.master: false 
node.voting_only: false 
node.data: false 
node.ingest: true 
node.ml: false 
cluster.remote.connect: false 
```

协调（coordinating）节点

如果您取消了处理主任务、保存数据和预处理文档的能力，那么您就只剩下一个协调节点，它只能路由请求、处理搜索reduce阶段和分发批量索引。本质上，只有协调节点的行为就像智能负载均衡器

通过将协调节点的角色从数据和符合主条件的节点中卸载出来，只协调节点可以使大型集群受益。它们加入集群并接收完整的集群状态，就像其他每个节点一样，它们使用集群状态将请求直接路由到适当的位置

在查询的时候，通常会涉及到从多个 node 服务器上查询数据，并将请求分发到多个指定的 node 服务器，并对各个 node 服务器返回的结果进行一个汇总处理，最终返回给客户端。在 ES 集群中，所有的节点都有可能是协调节点，但是，可以通过设置 `node.master`、`node.data`、`node.ingest` 等都为 `false` 来设置专门的协调节点。需要较好的 CPU 和较高的内存

```
node.master: false 
node.voting_only: false 
node.data: false 
node.ingest: false 
node.ml: false 
cluster.remote.connect: false 
```

