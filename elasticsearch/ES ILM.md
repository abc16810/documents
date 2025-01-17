ILM：管理索引生命周期

可以配置索引生命周期管理 (ILM) 策略，以根据您的性能、弹性和保留要求自动管理索引。  例如，您可以使用 ILM 来

- 当索引达到特定大小或文档数量时启动新索引
- 每天、每周或每月创建一个新索引并归档以前的索引
- 删除过时的索引以强制执行数据保留标准

您可以通过 Kibana Management 或 ILM API 创建和管理索引生命周期策略。  当您为 Beats 或 Logstash Elasticsearch 输出插件启用索引生命周期管理时，会自动配置默认策略



#### ILM 概述

可以创建和应用索引生命周期管理 (ILM) 策略，以根据您的性能、弹性和保留要求自动管理索引。

索引生命周期策略可以触发以下操作

- **Rollover**（翻转）：当当前索引达到特定大小、文档数量或年龄时，创建一个新的写入索引
- **Shrink**：减少索引中主分片的数量
- **Force merge**强制合并：触发强制合并以减少索引分片中的段数。
- **Freeze**冻结：冻结索引并使其只读
- **Delete**删除：永久删除索引，包括其所有数据和元数据

ILM 使管理热-暖-冷架构中的索引变得更加容易，这在您处理日志和指标等时间序列数据时很常见

- 您希望滚动到新索引的最大分片大小、文档数或年龄。
- 索引不再更新并且可以减少主分片数量的点
- 何时强制合并以永久删除标记为删除的文档
- 可以将索引移动到性能较低的硬件节点
- 可用性不那么关键并且可以减少副本数量的点
- 何时可以安全删除索引

例如：当索引的主分片的总大小达到 50GB 时，滚动到新索引。将旧索引移动到暖阶段，将其标记为只读，然后将其缩小为单个分片，7 天后，将索引移至冷阶段并将其移至更便宜的硬件。达到所需的 30 天保留期后，删除索引

注：要使用 ILM，集群中的所有节点都必须运行相同的版本。  尽管可以在混合版本集群中创建和应用策略，但不能保证它们会按预期工作。  尝试使用包含集群中所有节点不支持的操作的策略将导致错误

#### 索引生命周期

ILM 定义了五个索引生命周期阶段：

- **Hot**：正在积极更新和查询索引
- **Warm**：索引不再更新，但仍在查询中
- **Cold**： 该索引不再被更新并且很少被查询。  信息仍然需要可搜索，但如果这些查询速度较慢也没关系
- **Frozen **该索引不再被更新并且很少被查询。  这些信息仍然需要可搜索，但如果这些查询非常慢也没关系。
- **Delete** 不再需要该索引，可以安全地删除该索引。



**阶段转换**

最小年龄默认为零，这会导致 ILM 在当前阶段中的所有操作完成后立即将索引移动到下一阶段

如果索引有未分配的分片并且集群健康状态为黄色，该索引仍然可以根据其索引生命周期管理策略过渡到下一阶段。  但是，由于 Elasticsearch 只能在绿色集群上执行某些清理任务，因此可能会出现意想不到的副作用

**阶段执行**

当索引进入一个阶段时，ILM 将阶段定义缓存在索引元数据中。  这可确保策略更新不会将索引置于永远无法退出阶段的状态。  如果可以安全地应用更改，ILM 会更新缓存的阶段定义。  如果不能，阶段执行将继续使用缓存的定义。

ILM 定期运行，检查索引是否符合策略标准，并执行所需的任何步骤。  为避免竞争条件，ILM 可能需要多次运行才能执行完成操作所需的所有步骤。 例如，如果 ILM 确定索引已满足翻转条件，它会开始执行完成翻转操作所需的步骤。  如果它达到了不能安全地进入下一步的点，则执行停止。  下次ILM 运行时，ILM 会从中断处继续执行。  这意味着即使 `indices.lifecycle.poll_interval` 设置为 10 分钟并且索引符合翻转标准，也可能需要 20 分钟才能完成翻转

**阶段动作**

ILM 在每个阶段都支持以下操作。  ILM 按列出的顺序执行操作

- Hot
  -  [Set Priority](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-set-priority.html) 
  -  [Unfollow](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-unfollow.html) 
  -  [Rollover](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-rollover.html) 
  -  [Read-Only](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-readonly.html) 
  -  [Shrink](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-shrink.html) 
  -  [Force Merge](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-forcemerge.html) 
  -  [Searchable Snapshot](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-searchable-snapshot.html) 

- Warm
  -  [Set Priority](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-set-priority.html) 
  -  [Unfollow](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-unfollow.html) 
  -  [Read-Only](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-readonly.html) 
  -  [Allocate](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-allocate.html) 
  -  [Migrate](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-migrate.html) 
  -  [Shrink](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-shrink.html) 
  -  [Force Merge](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-forcemerge.html) 

- Cold
  -  [Set Priority](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-set-priority.html) 
  -  [Unfollow](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-unfollow.html) 
  -  [Read-Only](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-readonly.html) 
  -  [Searchable Snapshot](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-searchable-snapshot.html) 
  -  [Allocate](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-allocate.html) 
  -  [Migrate](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-migrate.html) 
  -  [Freeze](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-freeze.html) 

- Frozen 
  -  [Searchable Snapshot](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-searchable-snapshot.html)    (企业版，所以开源版不能配置Frozen阶段)

- Delete
  -  [Wait For Snapshot](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-wait-for-snapshot.html) 
  -  [Delete](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/ilm-delete.html) 

#### Rollover（翻转）

为了满足您的索引和搜索性能要求并管理资源使用情况，您写入索引直到满足某个阈值，然后创建一个新索引并开始写入它。  使用滚动索引使您能够

- 针对高性能热节点上的高摄取率优化活动索引
- 优化暖节点上的搜索性能
- 将较旧、访问频率较低的数据转移到成本较低的冷节点，
- 通过删除整个索引，根据您的保留策略删除数据

我们建议使用数据流来管理时间序列数据。  数据流自动跟踪写入索引，同时将配置保持在最低限度

每个数据流都需要一个索引模板，其中包含：

- 数据流的名称或通配符 (*) 模式
- 数据流的时间戳字段。  该字段必须映射为`date`或 `date_nanos`字段数据类型，并且必须包含在索引到数据流的每个文档中。
- 创建时应用于每个后备索引的映射和设置。

数据流专为仅附加数据而设计，其中数据流名称可用作操作（读取、写入、翻转、收缩等）目标。  如果您的用例需要就地更新数据，您可以改为使用索引别名来管理您的时间序列数据。  但是，还有一些配置步骤和概念

- 为系列中的每个新索引指定设置的索引模板。  您可以优化此配置以进行摄取，通常使用与热节点一样多的分片
- 引用整个索引集的索引别名。
- 指定为写入索引的单个索引。  这是处理所有写请求的活动索引。  在每次翻转时，新索引将成为写入索引。

#### 自动翻转

ILM 使您能够根据索引大小、文档计数或年龄自动滚动到新索引。  当触发翻转时，会创建一个新索引，写入别名会更新为指向新索引，所有后续更新都会写入新索引。



#### 生命周期策略更新

您可以通过修改当前策略或切换到不同的策略来更改索引或滚动索引集合的生命周期的管理方式

为确保策略更新不会将索引置于无法退出当前阶段的状态，阶段定义在进入阶段时缓存在索引元数据中。  如果可以安全地应用更改，ILM 会更新缓存的阶段定义。  如果不能，阶段执行将继续使用缓存的定义

当索引进入下一阶段时，它使用更新策略中的阶段定义。

对 min_age 的更改不会传播到缓存的定义。  更改阶段的 min_age 不会影响当前正在执行该阶段的索引。

例如，如果您创建的策略具有未指定 min_age 的热阶段，则索引会在应用策略时立即进入热阶段。  如果您随后更新策略以指定热阶段的 min_age 为 1 天，这对已经处于热阶段的索引没有影响。  政策更新后创建的索引在一天之内不会进入hot阶段

当您将不同的策略应用于管理索引时，索引会使用上一个策略中的缓存定义完成当前阶段。  索引在进入下一阶段时开始使用新策略。

#### 使用 ILM 自动翻转

要使用 ILM 自动翻转和管理数据流，必须定义如下步骤

- 创建定义适当阶段和操作的生命周期策略

- 创建索引模板以创建数据流并为支持索引应用 ILM 策略和索引设置和映射配置
- 验证索引是否按预期通过生命周期阶段

**1. 创建生命周期策略**

生命周期策略指定索引生命周期中的各个阶段以及要在每个阶段执行的操作。  一个生命周期最多可以有五个阶段：热、暖、冷、冻结和删除

例如，您可以定义一个包含两个阶段的 timeseries_policy

- 定义翻转操作的hot阶段，以指定索引在达到 50 GB 的 max_primary_shard_size 或 30 天的 max_age 时翻转
- 将 min_age 设置为在翻转 90 天后删除索引的删除阶段

您可以通过 Kibana 或使用创建或更新策略 API 创建策略。  要从 Kibana 创建策略，请打开菜单并转到堆栈管理 > 索引生命周期策略。  单击创建策略。

```
PUT _ilm/policy/timeseries_policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_age": "30d",
            "max_size": "50gb"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

**2. 创建索引模板以创建数据流并应用生命周期策略**

要设置数据流，首先创建一个索引模板来指定生命周期策略。  因为模板用于数据流，所以它还必须包含 data_stream 定义。

例如，您可以创建一个 timeseries_template 以用于名为 timeseries 的未来数据流。

为了使 ILM 能够管理数据流，模板配置了一个 ILM 设置：

- `index.lifecycle.name` 指定要应用于数据流的生命周期策略的名称

您可以使用 Kibana 创建模板向导来添加模板。  在 Kibana 中，打开菜单并转到堆栈管理 > 索引管理。  在索引模板选项卡中，单击创建模板。 API如下

```
PUT _index_template/timeseries_template
{
  "index_patterns": ["timeseries"],     # 当文档被索引到timeseries目标时应用模板               
  "data_stream": { },  #  该模板创建数据流，而非索引
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1,
      "index.lifecycle.name": "timeseries_policy"     # 指定ILM策略  
    }
  }
}
```

**3. 创建数据流**

首先，将文档索引到索引模板的` index_patterns` 中定义的名称或通配符模式。  只要现有数据流、索引或索引别名尚未使用该名称，索引请求就会自动创建具有单个后备索引的相应数据流。  Elasticsearch 自动将请求的文档索引到这个支持索引中，该索引也充当流的写入索引

例如，以下请求创建``timeseries` `数据流和名为 .ds-timeseries-2099.03.08-000001 的第一代支持索引

```
POST timeseries/_doc
{
  "message": "logged the request",
  "@timestamp": "1591890611"
}
```

当满足生命周期策略中的翻转条件时，翻转操作

- 创建名为 `.ds-timeseries-2099.03.08-000002 `的第二代支持索引。  因为它是`timeseries` 数据流的后备索引，所以来自 `timeseries_template` 索引模板的配置将应用于新索引
- 由于是`timeseries` 数据流的最新一代索引，新创建的后备索引` .ds-timeseries-2099.03.08-000002 `成为数据流的写入索引。

每次满足翻转条件时，都会重复此过程。  您可以使用` timeseries `数据流名称搜索由` timeseries_policy `管理的所有数据流的后备索引。  写操作被路由到当前的写索引。  读取操作将由所有后备索引处理

**4. 检查生命周期进度**

要获取管理索引的状态信息，请使用` ILM explain API`。  这使您可以了解以下内容

- 索引处于哪个阶段以及何时进入该阶段
- 当前操作以及正在执行的步骤。
- 如果发生任何错误或进度被阻止

例如，以下请求获取有关`timeseries` 数据流支持索引的信息：

```
GET .ds-timeseries-*/_ilm/explain
```

以下响应显示数据流的第一代后备索引正在等待热阶段的翻转操作。  它保持这种状态，并且 ILM 继续调用 check-rollover-ready，直到满足翻转条件

```
{

    "indices": {
        ".ds-timeseries-2022.06.10-000001": {
            "index": ".ds-timeseries-2022.06.10-000001",
            "managed": true,
            "policy": "timeseries_policy",  # 用于管理索引的策略
            "lifecycle_date_millis": 1654820331529,
            "age": "9.97m",   # 索引的年龄
            "phase": "hot",
            "phase_time_millis": 1654820331720,
            "action": "rollover",
            "action_time_millis": 1654820331920,
            "step": "check-rollover-ready",   # ILM 在索引上执行的步骤
            "step_time_millis": 1654820331920,
            "phase_execution": {
                "policy": "timeseries_policy",
                "phase_definition": {  # 当前阶段（热阶段）的定义
                    "min_age": "0ms",
                    "actions": {
                        "rollover": {
                            "max_size": "50gb",
                            "max_age": "30d"
                        },
                        "set_priority": {
                            "priority": 100
                        }
                    }
                },
                "version": 1,
                "modified_date_in_millis": 1654650073804
            }
        }
    }

}
```

#### 管理没有数据流的时间序列数据

尽管数据流是扩展和管理时间序列数据的便捷方式，但它们被设计为仅追加。  我们认识到可能存在需要更新或删除数据并且数据流不直接支持删除和更新请求的用例，因此需要直接在数据流的支持索引上使用索引 API。

在这些情况下，您可以使用索引别名来管理包含时间序列数据的索引并定期滚动到新索引

要使用索引别名通过 ILM 自动滚动和管理时间序列索引：

- 创建定义适当阶段和操作的生命周期策略。  请参阅上面的创建生命周期策略
- 创建索引模板以将策略应用于每个新索引
- 引导一个索引作为初始写入索引
- 验证索引是否按预期通过生命周期阶段

**1. 创建索引模板以应用生命周期策略**

例如，您可以创建一个` timeseries_template` 应用于名称与` timeseries-* `索引模式匹配的新索引

为了启用自动翻转，模板配置了两个 ILM 设置

- `index.lifecycle.name` 指定要应用于与索引模式匹配的新索引的生命周期策略的名称
- `index.lifecycle.rollover_alias` 指定在为索引触发翻转操作时要翻转的索引别名。

```
PUT _index_template/timeseries_template  
{
  "index_patterns": ["timeseries-*"],    # 如果索引名称以timeseries-开头，则将模板应用于改索引   
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1,
      "index.lifecycle.name": "timeseries_policy",      
      "index.lifecycle.rollover_alias": "timeseries"  # 用于引用这些索引的别名的名称。  对于使用翻转操作的策略是必需的。   
    }
  }
}
```

**2. 使用写入索引别名引导初始时间序列索引**

首先，您需要引导一个初始索引并将其指定为索引模板中指定的翻转别名的写入索引。  此索引的名称必须与模板的索引模式匹配并以数字结尾。  在翻转时，该值会递增以生成新索引的名称

例如，以下请求创建了一个名为 `timeseries-000001` 的索引，并使其成为` timeseries `别名的写入索引。

```
PUT timeseries-000001
{
  "aliases": {
    "timeseries": {
      "is_write_index": true
    }
  }
}
```

当满足翻转条件时，翻转动作

- 创建一个名为 timeseries-000002 的新索引。  这与 timeseries-* 模式匹配，因此 timeseries_template 中的设置将应用于新索引
- 将新索引指定为写入索引并使引导索引为只读

每次满足翻转条件时，都会重复此过程。  您可以使用 timeseries 别名搜索由 timeseries_policy 管理的所有索引。  写操作被路由到当前的写索引

**3. 检查生命周期进度**

检索托管索引的状态信息与数据流的情况非常相似。  有关详细信息，请参阅数据流检查进度部分。  唯一的区别是索引命名空间，因此检索进度将需要以下 api 调用

```
 GET timeseries-*/_ilm/explain
```



#### 索引生命周期操作(actions)

- **Allocate 分配** 将分片移动到具有不同性能特征的节点并减少副本数量 （允许的阶段：warm, cold）

  hot阶段不允许分配动作。  索引的初始分配必须手动或通过索引模板完成

  您必须指定副本数或至少一个包含、排除或要求选项。  空分配操作无效

  ```
  number_of_replicas  # （可选，整数）分配给索引的副本数
  total_shards_per_node # （可选，整数）单个 Elasticsearch 节点上索引的最大分片数。  值 -1 被解释为无限制
  include （可选）
  exclude （可选）
  require （可选）
  # 以下策略中的 allocate 操作将索引的副本数更改为 2。将不超过 200 个索引分片放置在任何单个节点上。  否则索引分配规则不会改变
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "warm": {
          "actions": {
            "allocate" : {
              "number_of_replicas" : 2,
              "total_shards_per_node" : 200
            }
          }
        }
      }
    }
  }
  ```

  **使用自定义属性为节点分配索引**

  以下策略中的分配操作将索引分配给 box_type 为 hot 或 warm 的节点（要指定节点的 box_type，请在节点配置中设置自定义属性。  例如，在 elasticsearch.yml 中设置 `node.attr.box_type: hot`）

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "warm": {
          "actions": {
            "allocate" : {
              "include" : {
                "box_type": "hot,warm"
              }
            }
          }
        }
      }
    }
  }
  ```

  **根据多个属性为节点分配索引**

  分配动作还可以基于多个节点属性为节点分配索引。  以下操作根据 `box_type` 和`storage` 节点属性分配索引

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "cold": {
          "actions": {
            "allocate" : {
              "require" : {
                "box_type": "cold",
                "storage": "high"
              }
            }
          }
        }
      }
    }
  }
  ```

  **将索引分配给特定节点并更新副本设置**

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "warm": {
          "actions": {
            "allocate" : {
              "number_of_replicas": 1,
              "require" : {
                "box_type": "cold"
              }
          }
          }
        }
      }
    }
  }
  ```

- **Delete**  永久删除索引（允许的阶段：delete）

  ```
  delete_searchable_snapshot # （可选，布尔值）删除在前一阶段创建的可搜索快照。  默认为真
  ```

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "delete": {
          "actions": {
            "delete" : { }
          }
        }
      }
    }
  }
  ```

- **Force merge** 减少索引（segments ）的数量并清除已删除的文档。  使索引只读。 (允许的阶段：hot, warm.)

  要在hot阶段使用 forcemerge 动作，必须存在`rollover` 动作。  如果未配置翻转操作，ILM 将拒绝该策略。

  强制合并是一项资源密集型操作。  如果一次触发过多的强制合并，可能会对您的集群产生负面影响。  当您将包含强制合并操作的 ILM 策略应用于现有索引时，可能会发生这种情况。  如果他们满足 min_age 标准，他们可以立即进行多个阶段。  您可以通过增加 min_age 或设置 index.lifecycle.origination_date 来更改索引年龄的计算方式来防止这种情况。

  如果您遇到强制合并任务队列积压，您可能需要增加强制合并线程池的大小，以便可以并行强制合并索引。  为此，请配置`thread_pool.force_merge.size` 集群设置

  ```
  max_num_segments # （必需，整数）要合并到的段数。  要完全合并索引，请设置为 1
  index_codec # （可选，字符串）用于压缩文档存储的编解码器。  唯一接受的值是 best_compression，它使用 DEFLATE 来获得更高的压缩率，但存储字段的性能会降低。  要使用默认 LZ4 编解码器，请省略此参数
  ```

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "warm": {
          "actions": {
            "forcemerge" : {
              "max_num_segments": 1
            }
          }
        }
      }
    }
  }
  ```

- **Freeze**  冻结索引以最小化其内存占用。(允许的阶段：cold)

  冻结索引会关闭索引并在同一个 API 调用中重新打开它。  这意味着在短时间内没有分配主分片。  集群将变红，直到分配了主分片。  将来可能会取消此限制。

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "cold": {
          "actions": {
            "freeze" : { }
          }
        }
      }
    }
  }
  ```

- **Migrate 迁移** 将索引分片移动到与当前 ILM 阶段对应的数据层  (允许的阶段：warm, cold)

  通过更新` index.routing.allocation.include._tier_preference `索引设置，将索引移动到与当前阶段对应的数据层。  如果分配操作未指定分配选项，ILM 会自动在暖阶段和冷阶段注入迁移操作。  如果您指定仅修改索引副本数的分配操作，ILM 会在迁移索引之前减少副本数。  要在不指定分配选项的情况下防止自动迁移，您可以显式包含迁移操作并将启用的选项设置为 false

  如果冷阶段定义了可搜索的快照操作，则迁移操作不会在冷阶段自动注入，因为管理索引将使用迁移操作配置的相同 _tier_preference 基础结构直接安装在目标层上。

  在暖阶段，迁移操作将` index.routing.allocation.include._tier_preference` 设置为 `data_warm,data_hot`。  这会将索引移动到暖层中的节点。  如果[warm tier](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/data-tiers.html#warm-tier) 没有节点，则回退到[hot tier](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/data-tiers.html#hot-tier).

  在冷阶段，迁移操作将` index.routing.allocation.include._tier_preference` 设置为 `data_cold、data_warm、data_hot`。  这会将索引移动到冷层中的节点。  
  如果冷层中没有节点，则回退到[warm](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/data-tiers.html#warm-tier)层，如果没有可用的warm节点，则回退到[hot](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/data-tiers.html#hot-tier) 层。	

  冻结阶段不允许迁移操作。  冻结阶段使用 data_frozen、data_cold、data_warm、data_hot 的 index.routing.allocation.include._tier_preference 直接挂载可搜索快照

  在 hot 阶段不允许执行 migrate 操作。  初始索引分配是自动执行的，可以手动配置或通过索引模板进行配置。

  ```
  enabled # （可选，布尔值）控制 ILM 是否在此阶段自动迁移索引。  默认为真
  ```

  在以下策略中，指定分配操作以在 ILM 将索引迁移到暖节点之前减少副本数量。

  不需要显式指定迁移操作 - ILM 会自动执行迁移操作，除非您指定分配选项或禁用迁移

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "warm": {
          "actions": {
            "migrate" : {
            },
            "allocate": {
              "number_of_replicas": 1
            }
          }
        }
      }
    }
  }
  ```

- **Read only**   阻止对索引的写入操作 （允许的阶段：hot, warm, cold）

  要在热阶段使用只读操作，必须存在翻转操作。  如果未配置翻转操作，ILM 将拒绝该策略。

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "warm": {
          "actions": {
            "readonly" : { }
          }
        }
      }
    }
  }
  ```

- **Rollover**  移除索引作为翻转别名的写入索引，并开始索引到新索引。（允许的阶段：hot）

  翻转目标可以是数据流或索引别名。  以数据流为目标时，新索引成为数据流的写入索引，并且其生成递增。

  要翻转索引别名，别名及其写入索引必须满足以下条件：

  - 索引名称必须与模式 ^.*-\d+$ 匹配，例如 (my-index-000001)。
  - `index.lifecycle.rollover_alias` 必须配置为别名才能翻转。
  - 该索引必须是别名的写入索引。

  例如，如果 my-index-000001 具有别名 my_data，则必须配置以下设置

  ```
  PUT my-index-000001
  {
    "settings": {
      "index.lifecycle.name": "my_policy",
      "index.lifecycle.rollover_alias": "my_data"
    },
    "aliases": {
      "my_data": {
        "is_write_index": true
      }
    }
  }
  ```

  ```
  max_age  # （可选，时间单位）在达到创建索引的最大经过时间后触发翻转
  max_docs # （可选，整数）在达到指定的最大文档数后触发翻转。  自上次刷新后添加的文档不包含在文档计数中。  文档计数不包括副本分片中的文档。
  max_size  #  （可选，字节单位）当索引达到一定大小时触发翻转。  这是索引中所有主分片的总大小。  副本不计入最大索引大小
  max_primary_shard_size # （可选，字节单位）当索引中最大的主分片达到一定大小时触发翻转。  这是索引中主分片的最大大小。  与 max_size 一样，副本被忽略
  ```

  ```
  # 根据最大主分片大小翻转 此示例在其最大主分片至少为 50 GB 时滚动索引
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "hot": {
          "actions": {
            "rollover" : {
              "max_primary_shard_size": "50GB"
            }
          }
        }
      }
    }
  }
  # 根据索引大小翻转 此示例在索引至少为 100 GB 时滚动索引
  ...
    "rollover" : {
              "max_size": "100GB"
            }
  ...
  # 此示例在索引包含至少一亿个文档时滚动索引
  "rollover" : {
              "max_docs": 100000000
            }
  # 如果索引至少在 7 天前创建，则此示例将滚动索引。
   "rollover" : {
              "max_age": "7d"
            }
  ```

- **Searchable snapshot**   在配置的存储库中拍摄管理索引的快照并将其挂载为可搜索的快照 （允许的阶段：hot, cold, frozen.）  （企业版支持）

- **Set priority**  （允许的阶段：hot, warm, cold） 

  只要策略进`hot, warm, 或者 cold`阶段，就设置索引的优先级。  在节点重新启动后，优先级较高的索引会在优先级较低的索引之前恢复

  一般来说，hot阶段的指标应取最高值，cold阶段的指标应取最低值。  例如：hot为 100，warm为 50，cold为 0。  未设置此值的索引的默认优先级为 1

  ```
  priority #（必需，整数）索引的优先级。  必须为 0 或更大。  设置为 null 以删除优先级
  ```

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "warm": {
          "actions": {
            "set_priority" : {
              "priority": 50
            }
          }
        }
      }
    }
  }
  ```

- **Shrink ** 通过将索引缩小为新索引来减少主分片的数量 (允许的阶段：hot, warm)

  将源索引设置为只读并将其缩小为具有较少主分片的新索引。  结果索引的名称是 `shrink-<random-uuid>-<original-index-name>`。  此操作对应于收缩 API。

  在收缩操作之后，任何指向源索引的别名都指向新的收缩索引。  如果 ILM 对数据流的后备索引执行收缩操作，收缩的索引将替换流中的源索引。  您不能对写入索引执行收缩操作

  要在hot阶段使用`shrink` 动作，必须存在`rollover` 动作。  如果未配置翻转操作，ILM 将拒绝该策略

  收缩操作将取消设置索引的 `index.routing.allocation.total_shards_per_node` 设置，这意味着没有限制。  这是为了确保索引的所有分片都可以复制到单个节点。  即使在该步骤完成后，此设置更改仍将保留在索引上

  ```
  number_of_shards # （可选，整数）要收缩到的分片数。  必须是源索引中分片数量的一个因素。  此参数与 max_primary_shard_size 冲突，只能设置其中一个。
  max_primary_shard_size # （可选，字节单位）目标索引的最大主分片大小。  用于查找目标索引的最佳分片数.该参数与设置中的 number_of_shards 冲突，只能设置其中一个
  ```

  ```
  # 显式设置新收缩索引的分片数
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "warm": {
          "actions": {
            "shrink" : {
              "number_of_shards": 1
            }
          }
        }
      }
    }
  }
  # 以下策略使用 max_primary_shard_size 参数根据源索引的存储大小自动计算新收缩索引的主分片数
  ...
  "warm": {
          "actions": {
            "shrink" : {
              "max_primary_shard_size": "50gb"
            }
          }
        }
  ```

  在收缩操作期间，ILM 将源索引的主分片分配给一个节点。  收缩索引后，ILM 会根据您的分配规则将收缩索引的分片重新分配到适当的节点。

  这些分配步骤可能因多种原因而失败，包括:

  - 在收缩操作期间删除一个节点
  - 没有节点有足够的磁盘空间来托管源索引的分片
  - 由于分配规则冲突，Elasticsearch 无法重新分配缩小的索引。

  当其中一个分配步骤失败时，ILM 会等待 `index.lifecycle.step.wait_time_threshold` 中设置的时间段，默认为 12 小时。  此阈值时间段允许集群解决导致分配失败的任何问题

  如果阈值期过后且 ILM 尚未缩小索引，则 ILM 会尝试将源索引的主分片分配给另一个节点。  如果 ILM 收缩索引但无法在阈值期间重新分配收缩索引的分片，则 ILM 会删除收缩索引并重新尝试整个收缩操作。

- **Unfollow**  将追随者索引转换为常规索引。  在翻转、收缩或可搜索快照操作之前自动执行 （允许的阶段：hot, warm, cold, frozen.）

  将 CCR 追随者索引转换为常规索引。  这使得收缩、翻转和可搜索的快照操作可以在跟随者索引上安全地执行。  在整个生命周期中移动追随者索引时，您也可以直接使用取消关注。  对不是跟随者的索引没有影响，阶段执行只是移动到下一个动作。

  >  当翻转、收缩和可搜索快照操作应用于追随者索引时，此操作会自动触发

  此操作会等到将追随者索引转换为常规索引是安全的。  必须满足以下条件

  - 领导者索引必须将` index.lifecycle.indexing_complete `设置为 true。  如果使用翻转操作翻转领导者索引，则会自动发生这种情况，并且可以使用索引设置 API 手动设置
  - 对领导者索引执行的所有操作都已复制到跟随者索引。  这可确保在转换索引时不会丢失任何操作

  一旦满足这些条件，取消关注将执行以下操作

  - 为跟随者索引暂停索引跟随。
  - 关闭跟随者索引
  - 取消关注领导者索引
  - 打开追随者索引（此时是常规索引）

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "hot": {
          "actions": {
            "unfollow" : {}
          }
        }
      }
    }
  }
  ```

- **Wait for snapshot**  在删除索引之前确保快照存在 （允许的阶段：delete）

  在删除索引之前等待执行指定的 SLM 策略。  这可确保已删除索引的快照可用

  ```
  policy   # （必需，字符串）删除操作应等待的 SLM 策略的名称。
  ```

  ```
  PUT _ilm/policy/my_policy
  {
    "policy": {
      "phases": {
        "delete": {
          "actions": {
            "wait_for_snapshot" : {
              "policy": "slm-policy-name"
            }
          }
        }
      }
    }
  }
  ```

  



####  配置生命周期策略

ILM策略存储在全局集群状态中，可以通过在快照时将`include_global_state`设置为true来包含在快照中。在恢复快照时，将恢复处于全局状态的所有策略，并覆盖任何具有相同名称的本地策略。

```
PUT _ilm/policy/my_policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_primary_shard_size": "25GB"  # 当索引大小达到25GB时，滚动索引
          }
        }
      },
      "delete": {
        "min_age": "30d",  # 翻转30天后删除索引
        "actions": {
          "delete": {} 
        }
      }
    }
  }
}
```

**手动应用生命周期策略**

您可以在创建索引或通过Kibana Management或更新设置API将策略应用到现有索引时指定策略。当您应用一个策略时，ILM立即开始管理索引。

```
PUT test-index
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "index.lifecycle.name": "my_policy" 
  }
}
```

**将策略应用于多个索引**

```
PUT mylogs-pre-ilm*/_settings 
{
  "index": {
    "lifecycle": {
      "name": "mylogs_policy_existing"
    }
  }
}
```

**切换索引的生命周期策略**

要切换索引的生命周期策略，请遵循以下步骤:

- 使用移除策略API移除现有策略。以数据流或别名为目标删除其所有索引的策略。

  ```
  POST logs-my_app-default/_ilm/remove
  ```

- 删除策略API从索引中删除所有ILM元数据，并且不考虑索引的生命周期状态。这会使索引处于不希望的状态。

  例如，“强制合并”动作会暂时关闭一个索引，然后重新打开它。在强制合并期间移除索引的ILM策略会使索引无限期关闭

  删除策略后，使用get索引API检查索引的状态。以数据流或别名为目标获取其所有索引的状态。

  ```
  GET logs-my_app-default
  ```

  然后可以根据需要更改索引。例如，您可以使用开放索引API重新打开任何封闭索引

  ```
  POST logs-my_app-default/_open
  ```

- 使用更新设置API分配新策略。以数据流或别名为目标，为其所有索引分配策略

  ```
  PUT logs-my_app-default/_settings
  {
    "index": {
      "lifecycle": {
        "name": "new-lifecycle-policy"
      }
    }
  }
  ```



#### 将索引分配过滤器迁移到节点角色

如果您目前使用自定义节点属性和基于属性的分配过滤器在热-暖-冷架构中的数据层中移动索引，我们建议您切换到使用内置节点角色和自动数据层分配。通过使用节点角色，ILM可以自动在数据层之间移动索引。

**对新索引强制一个默认首选项层**

设置`cluster.routing.allocation。enforce_default_tier_preference = true`确保新创建的索引将具有一个_tier_preference，覆盖创建索引API或关联的索引模板，如果其中任何一个为该设置指定了null。

**为现有索引设置层首选项**

ILM通过向每个阶段自动注入迁移操作，在可用数据层中自动转换托管索引

为了使ILM能够在数据层中移动一个已有的托管索引，将索引设置更新为:

- 通过将自定义分配筛选器设置为空来删除它。
- 设置`tier preference. `

例如，如果您的旧模板将data属性设置为hot以将碎片分配到热层，则将data属性设置为null并将_tier_preference设置为data_hot

```
PUT my-index/_settings
{
  "index.routing.allocation.require.data": null,
  "index.routing.allocation.include._tier_preference": "data_hot"
}
```

对于已经从热阶段过渡出来的索引，层首选应包括适当的回退层，以确保在首选层不可用时能够分配索引碎片。例如，将hot层指定为已经处于warm阶段的索引的回退层。

```
PUT my-index/_settings
{
  "index.routing.allocation.require.data": null,
  "index.routing.allocation.include._tier_preference": "data_warm,data_hot"
}
```

如果一个索引已经处于冷阶段，则包括冷、暖和热层。

对于同时具有`_tier_preference`和`require.data`的索引配置，但是`_tier_preference`过时了。节点属性配置比配置的`_tier_preference`“更冷”)，迁移需要删除`require.data`属性并更新`_tier_preference`以反映正确的分级

例如：对于具有以下路由配置的索引

```
{
  "index.routing.allocation.require.data": "warm",
  "index.routing.allocation.include._tier_preference": "data_hot"
}
```

路由配置应该像这样固定

```
PUT my-index/_settings
{
  "index.routing.allocation.require.data": null,
  "index.routing.allocation.include._tier_preference": "data_warm,data_hot"
}
```

#### 索引生命周期管理错误的疑难解答

当ILM执行生命周期策略时，在对某个步骤执行必要的索引操作时，可能会发生错误。当发生这种情况时，ILM将索引移动到ERROR步骤。如果ILM不能自动解决错误，执行将暂停，直到解决了策略、索引或集群的基本问题

例如，您可能有一个收缩索引策略，一旦一个索引至少有5天历史，就会将其收缩为4个分片:

```
PUT _ilm/policy/shrink-index
{
  "policy": {
    "phases": {
      "warm": {
        "min_age": "5d",
        "actions": {
          "shrink": {
            "number_of_shards": 4
          }
        }
      }
    }
  }
}
```

没有什么可以阻止您将收缩索引策略应用到只有两个分片的新索引:

```
PUT /my-index-000001
{
  "settings": {
    "index.number_of_shards": 2,
    "index.lifecycle.name": "shrink-index"
  }
}
```

五天后，ILM试图将my-index-000001从两个碎片缩小到四个碎片。由于收缩操作不能增加分片数，导致该操作失败，ILM将my-index-000001移到ERROR步骤

你可以使用ILM Explain API来获取错误的信息:

```
GET /my-index-000001/_ilm/explain
```

为了解决这个问题，你可以更新策略，在5天后将索引缩小到单个碎片:

```
PUT _ilm/policy/shrink-index
{
  "policy": {
    "phases": {
      "warm": {
        "min_age": "5d",
        "actions": {
          "shrink": {
            "number_of_shards": 1
          }
        }
      }
    }
  }
}
```

**重试失败的生命周期策略步骤**，一旦你修复了ERROR步骤中放置索引的问题，你可能需要显式地告诉ILM重试该步骤

```
POST /my-index-000001/_ilm/retry
```

ILM随后试图重新运行失败的步骤。您可以使用ILM Explain API来监视进度

#### 常见的ILM错误

- 翻转别名[x]可以指向多个索引，在索引模板[z]中发现重复的别名[x]

  目标翻转别名在索引模板的`index.lifecycle.rollover_alias` 设置。在引导初始索引时，需要显式配置此别名一次。然后，翻转操作管理别名的设置和更新，以便滚动到每个后续索引

  不要在索引模板的别名部分显式配置相同的别名。

- 设置`index.lifecycle.rollover_alias`索引[y]的Rollover_alias为空或未定义

  `index.lifecycle.rollover_alias`必须配置Rollover_alias设置才能使翻转操作生效

- 别名[x]有多个写索引[y,z]

  只能将一个索引指定为特定别名的写索引。使用alias API设置`is_write_index:false`除一个索引外的所有索引

- 索引名[x]与模式^.*-\d+不匹配

  索引名必须匹配regex模式`^.*-\d+`使翻转动作生效。最常见的问题是索引名不包含末尾数字。例如，my-index不符合模式需求

  在索引名称后面附加一个数字值，例如my-index-000001



#### 启动和停止索引生命周期管理

缺省情况下，ILM服务的状态为RUNNING，管理所有具有生命周期策略的索引

您可以停止索引生命周期管理，暂停所有索引的管理操作。例如，在执行预定的维护或对集群进行可能影响ILM操作执行的更改时，可能会停止索引生命周期管理。

注：当停止ILM时，SLM操作也会暂停。在重新启动ILM之前，不会按照计划进行快照。正在执行的快照不受影响。

要查看ILM服务的当前状态，可以使用Get status API:

```
GET _ilm/status
# 常运行时，响应显示ILM处于RUNNING状态:
{
  "operation_mode": "RUNNING"
}
```

停止ILM服务和暂停所有生命周期策略的执行，使用stop API:

```
POST _ilm/stop
```

ILM服务将所有策略运行到一个可以安全停止的位置。当ILM服务关闭时，状态API显示ILM处于停止模式:

```
{
  "operation_mode": "STOPPING"
}
```

一旦所有的策略都在安全的停止点，ILM就会进入停止模式:

```
{
  "operation_mode": "STOPPED"
}
```

要重新启动ILM并恢复执行策略，请使用Start API。这将使ILM服务处于RUNNING状态，ILM从它停止的位置开始执行策略。

```
POST _ilm/start
```

#### 管理现有索引

如果你一直在使用Curator 或其他机制来管理周期性索引，当你迁移到ILM时，你有两个选择:

- 设置索引模板，使用ILM策略来管理新索引。一旦ILM管理了当前的写索引，您就可以对旧索引应用适当的策略。
- 重新索引到一个ilm管理的索引

转换到使用ILM管理周期性索引的最简单方法是配置一个索引模板，以便将生命周期策略应用于新索引。一旦要写入的索引被ILM管理，就可以手动将策略应用到旧索引上

为旧索引定义一个单独的策略，该策略省略了翻转操作。翻转是用来管理新数据的位置，所以不适用。

请记住，应用于现有索引的策略将每个阶段的min_age与索引的原始创建日期进行比较，并可能立即执行多个阶段。如果您的策略执行强制合并等资源密集型操作，那么在切换到ILM时，您不希望有很多索引同时执行这些操作。

您可以在为现有索引使用的策略中指定不同的min_age值，或者设置`index.lifecycle.origination_date`来控制如何计算索引年龄

一旦所有pre-ILM索引都过时并被删除，您就可以删除用于管理它们的策略。

#### 跳过翻转

当`index.lifecycle.indexing_complete`设置为true, ILM将不会对索引执行翻转操作，即使它在其他方面满足翻转条件。当翻转动作成功完成时，由ILM自动设置

如果您需要对正常的生命周期策略进行异常处理并更新别名以强制进行滚转，但希望ILM继续管理索引，则可以手动设置它来跳过滚转。如果您使用翻转API。不需要手动配置此设置

如果删除索引的生命周期策略，此设置也会被删除。

例如，如果您需要更改一系列新索引的名称，同时按照您配置的策略保留以前索引的数据，您可以:

1. 为使用相同策略的新索引模式创建一个模板。
2. 引导初始索引
3. 使用别名API将别名的写索引更改为引导索引。
4. 设置`index.lifecycle.indexing_complete`为true在旧索引上表示它不需要滚转

ILM将继续按照您的现有策略管理旧索引。新的索引按照新的模板命名，按照相同的策略进行不间断管理



#### 恢复托管数据流或索引

当您恢复一个托管索引或带有托管备份索引的数据流时，ILM会自动恢复执行恢复后的索引的策略。恢复索引的min_age是相对于它最初创建或滚转的时间，而不是它的恢复时间。无论是否从快照恢复索引，策略操作都按照相同的时间表执行。如果您恢复一个索引，该索引在其长达一个月的生命周期的一半被意外删除，那么它将正常地在生命周期的最后两周继续进行

在某些情况下，您可能希望阻止ILM立即对恢复的索引执行其策略。例如，如果您正在恢复一个旧快照，您可能希望防止它在其生命周期的所有阶段快速发展。您可能希望在文档被标记为只读或收缩之前添加或更新文档，或者防止索引立即被删除。

使用实例防止ILM执行恢复后的索引策略

- 暂时停止ILM。这将暂停所有ILM策略的执行。
- 恢复快照
- 在ILM恢复策略执行之前，从索引中删除策略或执行任何您需要的操作。
- 重启ILM以恢复策略执行