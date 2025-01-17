#### 索引级别分片分配过滤

**碎片分配过滤**碎片分配过滤允许您指定允许哪些节点托管特定索引的碎片。这些per-index过滤器与集群范围的分配过滤和分配感知一起应用

分片分配过滤器可以基于自定义节点属性，也可以基于内置的`_name`、`_host_ip`、`_publish_ip`、`_ip`、`_host`、`_id`、`_tier`和`_tier_preference`属性。索引生命周期管理使用基于自定义节点属性的过滤器来决定在阶段之间移动时如何重新分配分片

|             |                                          |
| ----------- | ---------------------------------------- |
| _name       | 根据节点名称匹配节点                     |
| _host_ip    | 根据主机IP地址(与主机名关联的IP)匹配节点 |
| _publish_ip | 通过发布IP地址匹配节点                   |
| _ip         | 匹配_host_ip或_publish_ip                |
| _host       | 通过主机名匹配节点                       |
| _id         | 根据节点id匹配节点                       |
| _tier       | 根据节点的数据层角色匹配节点             |

```
# 在指定属性值时可以使用通配符
PUT test/_settings
{
  "index.routing.allocation.include._ip": "192.168.2.*"
}
```



`cluster.routing.allocation`设置是动态的，使活动索引能够从一组节点移动到另一组节点。**分片只有在不打破另一个路由约束的情况下才会被重新分配**，例如永远不会在同一个节点上分配一个主碎片和一个复制碎片

例如，您可以使用自定义节点属性来指示节点的性能特征，并使用分片分配过滤将特定索引的分片路由到最合适的硬件类

1. 可以在启动时为每个节点分配任意的元数据属性  指定属性rack为rack1，size为big

```
- node.attr.rack=rack1
- node.attr.size=big
# bin/elasticsearch -Enode.attr.rack=rack1 -Enode.attr.size=big
```

2. 向索引添加一个路由分配过滤器 `index.routing.allocation`支持三种类型的过滤器`include`, `exclude`, 和 `require` (设置是动态的)

   - `index.routing.allocation.include.{attribute}` 将索引分配给具有至少一个逗号分隔值的{属性}的节点。
   - `index.routing.allocation.require.{attribute}`将索引分配给一个具有所有逗号分隔值的节点
   - `index.routing.allocation.exclude.{attribute}`排除

   例如，要告诉Elasticsearch将测试索引中的分片分配给大节点或中节点，请使用`index.routing.allocation.include`

```
PUT test/_settings
{
  "index.routing.allocation.include.size": "big,medium"
}
```

或者，我们可以使用排除规则将索引test从小节点移开

```
PUT test/_settings
{
  "index.routing.allocation.exclude.size": "small"
}
```

可以指定多个规则，在这种情况下，必须满足所有条件。例如，我们可以将索引test移动到rack1中的大节点，如下所示

```
PUT test/_settings
{
  "index.routing.allocation.include.size": "big",
  "index.routing.allocation.include.rack": "rack1"
}
```

**延迟分配**

当一个节点出于某种原因(有意的或其他原因)离开集群时，主节点的反应是

1）提升一个复制碎片为主分片，以替换节点上的所有主节点

2）分配复制碎片以替换丢失的副本(假设有足够的节点)

3）重新平衡剩余节点的碎片

这些操作旨在通过确保尽快完全复制每个碎片来保护集群不受数据丢失的影响。

即使我们在[node level](https://www.elastic.co/guide/en/elasticsearch/reference/current/recovery.html)和[cluster level](https://www.elastic.co/guide/en/elasticsearch/reference/current/shards-allocation.html),都抑制并发恢复，这种“分片转移”仍然会给集群带来大量额外的负载，如果丢失的节点可能很快就会返回，这可能是不必要的。设想一下这样的情景:

- 节点5失去网络连接。

- 主节点为节点5上的每个主分片提升一个复制分片到主分片

- 主节点将新的副本分配给集群中的其他节点。
- 每个新副本在网络中生成一个主碎片的完整副本。
- 将更多的碎片移动到不同的节点以重新平衡集群。
- 节点5几分钟后返回。
- 主节点通过将碎片分配到节点5来重新平衡集群。

如果主节点只等待了几分钟，那么丢失的分片可以以最小的网络流量重新分配给节点5。对于已经自动同步刷新的空闲分片(不接收索引请求的分片)，这个过程甚至会更快

由于节点已经离开而未分配的副本碎片的分配可以通过`index.unassigned.node_left.delayed_timeout`动态设定  默认1m

````
# 更新活动索引(或所有索引):
PUT _all/_settings
{
  "settings": {
    "index.unassigned.node_left.delayed_timeout": "5m"
  }
}
````

启用延迟分配后，上面的场景将如下所示

- 节点5网络不通
- 主节点为节点5上的每个主分片提升一个复制分片到主分片。
- 主服务器记录一条消息，表示未分配的分片的分配已经延迟，以及延迟了多长时间
- 集群保持黄色，因为有未分配的副本碎片。
- 节点5在超时前几分钟返回
- 丢失的副本将重新分配给节点5(同步刷新的碎片几乎立即恢复)。

如果延迟分配超时，master将丢失的分片分配给另一个节点，该节点将开始恢复。如果丢失的节点重新加入集群，并且它的shard仍然具有与主分片相同的sync-id，则shard重定位将被取消，同步的shard将被用于恢复

被此超时设置延迟分配的分片数量可以通过集群健康状况API查看

```
GET _cluster/health 
# delayed_unassigned_shards
```

永久移除一个节点，如果一个节点不返回，而您希望使用Elasticsearch立即分配丢失的碎片，只需将超时更新为零:

```
PUT _all/_settings
{
  "settings": {
    "index.unassigned.node_left.delayed_timeout": "0"
  }
}
```

**恢复优先级**

如果可能，将按优先级顺序恢复未分配的碎片。索引按优先级排序如下

- 可选的`index.priority`设置(先高后低)
- 索引创建日期(先高后低)
- 索引名(先高后低)

这意味着，默认情况下，较新的索引将在较旧的索引之前恢复。

使用per-index可动态更新的索引。优先级设置自定义索引的优先级顺序。例如

```
PUT index_3
{
  "settings": {
    "index.priority": 10
  }
}
PUT index_4
{
  "settings": {
    "index.priority": 5
  }
}
# 更新
PUT index_4/_settings
{
  "index.priority": 1
}
```

**节点总碎片**

集群级的分配器试图将单个索引的分片分散到尽可能多的节点上。然而，取决于您有多少分片和索引，以及它们的大小，可能并不总是能够均匀地分布碎片。

下面的动态设置允许您指定每个节点所允许的单个索引的碎片总数的硬限制

```
index.routing.allocation.total_shards_per_node # 分配给单个节点的最大碎片数(副本和主碎片)。默认为无限
```

您还可以限制节点可以拥有的碎片的数量(集群级别控制)

```
cluster.routing.allocation.total_shards_per_node # 分配给每个节点的主片和复制片的最大数量。默认为-1(无限)
```



#### 集群级别碎片分配

碎片分配是将碎片分配给节点的过程。这可能发生在初始恢复、副本分配、重新平衡或添加或删除节点时

master的主要角色之一是决定将哪些分片分配给哪些节点，以及何时在节点之间移动分片，以平衡集群

- 集群级别的分片分配设置控制分配和重新平衡操作。
- 基于磁盘的分片分配设置解释了Elasticsearch如何考虑可用磁盘空间，以及相关设置。
- 分片分配感知和强制感知控制如何将分片分布到不同的机架或可用分区
- 集群级别的分片分配过滤允许某些节点或节点组被排除在分配之外，以便它们可以退役。



**集群级的分片分配设置**

 ```
# （下述都为动态配置）
cluster.routing.allocation.enable # 启用或禁用特定类型的分片分配 
    all - (默认)允许对所有类型的分片进行分配。  
    primaries - 只允许主分片分配分片。  
    new_primaries - 对于新的索引，只允许主分片分配。  
    none - 任何索引都不允许进行任何类型的分片分配  
cluster.routing.allocation.node_concurrent_incoming_recoveries  # 节点上最大接受的分片恢复并发数。一般指分片从其它节点恢复至本节点 默认2
cluster.routing.allocation.node_concurrent_outgoing_recoveries # 节点上最大发送的分片恢复并发数。一般指分片从本节点恢复至其它节点。 默认2
cluster.routing.allocation.node_concurrent_recoveries # 上述两个配置的快捷方式
cluster.routing.allocation.node_initial_primaries_recoveries # 副本的恢复是通过网络进行的，而节点重启后对未分配的主节点的恢复则使用来自本地磁盘的数据。这些恢复应该很快，这样就可以在同一个节点上并行地进行更多的初始主恢复 默认4
cluster.routing.allocation.same_shard.host # 如果为true，禁止将一个分片的多个副本分配给同一主机上的不同节点，即具有相同网络地址的节点。默认值为false，意味着shard的副本有时会分配给同一主机上的节点。只有在每台主机上运行多个节点时，此设置才有意义
 ```

为了加快集群恢复的速度，可以调整分片恢复并发数和本地初始化主恢复

**碎片重平衡设置**

当集群的每个节点上有相同数量的分片，而没有任何节点上的任何索引的分片集中时，集群就是平衡的。Elasticsearch运行一个称为再平衡的自动过程，它在集群中的节点之间移动分片，以提高其平衡。

再平衡遵循所有其他分片分配规则，如分配过滤和强制感知，这可能会阻止它完全平衡集群。在这种情况下，重新平衡力求在您配置的规则范围内实现最平衡的集群。如果您使用的是数据层，那么Elasticsearch自动应用分配过滤规则，将每个分片放置在适当的层中。这些规则意味着平衡器在每一层中独立工作。

```
# （下述都为动态配置）
cluster.routing.rebalance.enable # 启用或禁用针对特定类型的分片的重新平衡
    all - (默认)允许所有类型的碎片平衡。  
    primaries - 只允许主碎片进行分片平衡。  
    replicas - 只允许副本碎片平衡。  
    none - 任何索引都不允许进行任何类型的分片平衡。  
cluster.routing.allocation.allow_rebalance # 指定何时允许分片重新平衡
    always - 总是
    indices_primaries_active - 仅当集群中的所有主节点都被分配时。  
    indices_all_active - (默认)仅当集群中的所有分片(主、副本)都被分配时。  
cluster.routing.allocation.cluster_concurrent_rebalance #允许控制集群范围内允许多少并发分片重平衡。默认为2。请注意，此设置仅控制由于集群中的不平衡而导致的并发分片重定位的数量。此设置不限制由于分配过滤或强制感知而进行的分片重分配。
```

再平衡是通过根据每个节点的分片分配计算每个节点的权重，然后在节点之间移动分片，以减少较重节点的权重，增加较轻节点的权重。当不存在可能使任何节点的权值与其他节点的权值更接近超过可配置阈值的分片移动时，集群是平衡的。下面的设置允许您控制这些计算的细节。

```
# （下述都为动态配置）
cluster.routing.allocation.balance.shard #定义一个节点上分配的分片总数的权重因子(float)。默认为0.45f。提高这个值会使集群中所有节点的分片数量趋于均衡
cluster.routing.allocation.balance.index #为特定节点(float)上分配的每个索引的分片数量定义权重因子。默认为0.55度。提高这个值会使集群中所有节点的每个索引的分片数量趋于均衡。
cluster.routing.allocation.balance.threshold #应该执行的最小优化值(非负浮点数)。默认为1.0度。提高这个值将导致集群在优化分片平衡方面不那么积极
```

**基于磁盘碎片分配**

在决定是否将新的碎片分配到该节点或主动地将碎片从该节点重新定位之前，Elasticsearch将考虑节点上的可用磁盘空间

基于磁盘的分片分配器触发的分片移动也必须满足所有其他分片分配规则，如分配过滤和强制感知。如果这些规则过于严格，它们还可以防止碎片移动，以保持节点的磁盘使用在控制之下。如果您正在使用数据层，那么Elasticsearch将自动配置分配过滤规则，将分片放置在适当的层中，这意味着基于磁盘的分片分配程序在每个层中独立工作。

如果一个节点将磁盘填满的速度比Elasticsearch将碎片移到其他地方的速度快，那么就存在磁盘将被完全填满的风险。为了防止这种情况，作为最后的手段，一旦磁盘使用率达到洪峰位，Elasticsearch将阻塞对受影响节点上的shard索引的写操作。它还将继续将分片移动到集群中的其他节点上。当受影响节点磁盘占用率低于高位时，Elasticsearch将自动删除该节点的写块。

```
# （下述都为动态配置）
cluster.routing.allocation.disk.threshold_enabled # 默认值为true。设置为false禁用磁盘分配
cluster.routing.allocation.disk.watermark.low # 控制磁盘使用的低位。它的默认值是85%，这意味着Elasticsearch不会为磁盘使用率超过85%的节点分配分片。它也可以设置为一个绝对字节值(比如500mb)，以防止Elasticsearch在小于指定的可用空间量时分配分片。这个设置对新创建的索引的主分片没有影响，但是会阻止它们的副本被分配。
cluster.routing.allocation.disk.watermark.high # 控制高位。默认值为90%，这意味着Elasticsearch将尝试从磁盘使用率超过90%的节点上重新分配碎片。它还可以设置为一个绝对字节值(类似于低位)，以便在节点的空闲空间小于指定数量时将碎片从节点上重新定位。此设置影响所有分片的分配，无论之前是否分配
cluster.routing.allocation.disk.watermark.flood_stage #  控制洪峰位，默认值为95%。Elasticsearch对每个索引强制一个只读索引块(index.blocks.read_only_allow_delete)，该索引在节点上分配了一个或多个shard，并且至少有一个磁盘超过了磁盘的流量阶段。此设置是防止节点耗尽磁盘空间的最后手段。当硬盘利用率低于高水位时，索引块会被自动释放
cluster.info.update.interval #Elasticsearch应该多久检查一次集群中每个节点的磁盘使用情况。默认为30s
```

注：百分比值是指已使用的磁盘空间，而字节值是指可用的磁盘空间

以每分钟更新集群信息为例，将低位更新为至少100g、高位更新为至少50g、洪峰位更新为10g。

```
PUT _cluster/settings
{
  "persistent": {
    "cluster.routing.allocation.disk.watermark.low": "100gb",
    "cluster.routing.allocation.disk.watermark.high": "50gb",
    "cluster.routing.allocation.disk.watermark.flood_stage": "10gb",
    "cluster.info.update.interval": "1m"
  }
}
```

**碎片分配感知**

您可以使用自定义节点属性作为感知属性，以使Elasticsearch在分配分片时考虑到您的物理硬件配置。如果Elasticsearch知道哪些节点在相同的物理服务器上，在相同的机架中，或在相同的区域中，它可以分发主碎片和它的副本碎片，以最大限度地降低故障时丢失所有碎片副本的风险。

当通过dynamic `cluster.routing.allocation.awareness.attributes`设置启用shard分配感知时，shard只被分配给那些设置了指定感知属性值的节点。如果您使用多个感知属性，那么在分配分片时，Elasticsearch将单独考虑每个属性,类似于索引分配

启用分片分配感知功能

- 使用自定义节点属性指定每个节点的位置。例如，如果您希望Elasticsearch在不同机架上分发分片，您可以在每个节点的Elasticsearch.yml中配置文件设置一个名为rack_id的感知属性 `node.attr.rack_id: rack_one`

- 告诉Elasticsearch在分配分片时，通过在每个主节点的Elasticsearch.yml中配置文件设置`cluster.routing.allocation.awareness.attributes`来考虑一个或多个感知属性

   `cluster.routing.allocation.awareness.attributes: rack_id`

**强制感知**

默认情况下，如果一个位置失败，Elasticsearch会将所有丢失的复制碎片分配给其余的位置。虽然您可能在所有位置上都有足够的资源来托管主碎片和复制碎片，但单个位置可能无法托管所有碎片

为了防止单个位置在发生故障时超载，你可以设置`cluster.routing.allocation.awareness.force`，这样在另一个位置有可用的节点之前，副本不会被分配

例如，如果你有一个感知属性zone，并在zone1和zone2中配置节点，你可以使用强制感知来阻止Elasticsearch在只有一个zone可用的情况下分配副本:

```
cluster.routing.allocation.awareness.attributes: zone
cluster.routing.allocation.awareness.force.zone.values: zone1,zone2
```

**碎片分配过滤**

您可以使用集群级别的分片分配过滤器来控制Elasticsearch从任何索引分配分片的位置。这些集群范围的过滤器与逐索引分配过滤和分配感知一起应用,类似索引级别的分配过滤

集群级别的分片分配过滤最常见的用例是当您想让一个节点退役时。要在关闭节点之前将分片移出该节点，可以创建一个过滤器，通过IP地址排除该节点

```
PUT _cluster/settings
{
  "persistent" : {
    "cluster.routing.allocation.exclude._ip" : "10.0.0.1"
  }
}
```

**其它群集设置**

```
# Metadata 下述都为动态配置
cluster.blocks.read_only  # 使整个集群只读(索引不接受写操作)，不允许修改元数据(创建或删除索引)
cluster.blocks.read_only_allow_delete  # 只读但可以删除   
cluster.max_shards_per_node  # 每个节点限制集群的主碎片和复制碎片的总数
Elasticsearch拒绝任何创建超过此限制的分片的请求。例如，一个集群中有一个cluster.max_shards_per_node设置为100,3个数据节点分片限制为300。如果集群中已经有296个分片，Elasticsearch会拒绝向集群中添加5个或更多分片的请求。 默认1000
cluster.max_shards_per_node * number of non-frozen data nodes
cluster.max_shards_per_node.frozen  # 限制集群中冻结的主碎片和副本碎片的总数  默认3000
```

**用户自定义集群元数据**

用户定义的元数据可以使用Cluster Settings API存储和检索。这可以用于存储关于集群的任意、不经常更改的数据，而不需要创建索引来存储这些数据。该数据可以使用任何前缀为`cluster.metadata.`.的键来存储

```
PUT /_cluster/settings
{
  "persistent": {
    "cluster.metadata.administrator": "sysadmin@example.com"
  }
}
```

**索引墓碑**

集群状态维护索引墓碑，以显式地表示已删除的索引。在集群状态下维护的墓碑数量由以下设置控制

```
cluster.indices.tombstones.size # 默认500  (静态配置)
```

**日志**

控制日志记录的设置可以用`logger.`前缀动态更新

```
PUT /_cluster/settings
{
  "persistent": {
    "logger.org.elasticsearch.indices.recovery": "DEBUG"
  }
}
```

**持久任务**

每次创建持久任务时，主节点负责将任务分配给集群的一个节点，然后被分配的节点将接收任务并在本地执行它。为节点分配持久任务的过程由以下属性控制，可以动态更新

```
# 动态配置
cluster.persistent_tasks.allocation.enable  # 默认all 此设置不会影响已经执行的持久任务。只有新创建的持久任务或必须重新分配的任务(例如，在节点离开集群后)才会受到此设置的影响
cluster.persistent_tasks.allocation.recheck_interval # 控制执行分配检查以对这些因素作出反应的频率。缺省值是30秒。最小允许值为10秒。
```



#### 集群路由（Cluster Reroute）

重新路由命令允许手动更改集群中单个碎片的分配。例如，可以显式地将碎片从一个节点移动到另一个节点，可以取消分配，可以显式地将未分配的碎片分配给特定的节点（副本碎片）

查看分片的分布

```
curl  -X GET http://localhost:9200/_cluster/state/routing_table?pretty
```

响应包含解释为什么可以或不能执行命令。

```
curl -H "Content-Type: application/json"  -X GET http://localhost:9200/_cluster/allocation/explain?pretty -d '{"index": "myindex","shard": 0,"primary": true}
```





