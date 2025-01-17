数据流允许您跨多个索引存储仅附加的时间序列数据，同时为您提供单个命名资源用于请求。  数据流非常适合日志、事件、指标和其他连续生成的数据。

您可以将索引和搜索请求直接提交到数据流。  流自动将请求路由到存储流数据的支持索引。  您可以使用索引生命周期管理 (ILM) 来自动管理这些支持索引。  例如，您可以使用 ILM 自动将较旧的支持索引移动到成本较低的硬件并删除不需要的索引。  随着数据的增长，ILM 可以帮助您降低成本和开销。

#### Backing indices

数据流由一个或多个隐藏的、自动生成的支持索引组成

![backing indices](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/images/data-streams/data-streams-diagram.svg)

数据流需要匹配的索引模板。  该模板包含用于配置流的支持索引的映射和设置。

索引到数据流的每个文档都必须包含一个 @timestamp 字段，映射为`date`或 `date_nanos` 字段类型。  如果索引模板没有为@timestamp 字段指定映射，Elasticsearch 会将@timestamp 映射为具有默认选项的日期字段

同一个索引模板可以用于多个数据流。  您不能删除数据流正在使用的索引模板

#### 读请求

当您向数据流提交读取请求时，该流会将请求路由到其所有支持索引

![data streams search request](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/images/data-streams/data-streams-search-request.svg)

#### 写索引

最近创建的后备索引（backing index）是数据流的写入索引。  该流仅将新文档添加到此索引

![data streams index request](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/images/data-streams/data-streams-index-request.svg)

即使直接向索引发送请求，您也无法将新文档添加到其他支持索引

您也不能对可能妨碍索引的写入索引执行操作，例如：

-  [Clone](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/indices-clone-index.html) 
-  [Delete](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/indices-delete-index.html) 
-  [Freeze](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/freeze-index-api.html) 
-  [Shrink](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/indices-shrink-index.html) 
-  [Split](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/indices-split-index.html) 

#### Rollover （翻转）

翻转创建一个新的后备索引，该索引成为流的新写入索引

我们建议在写入索引达到指定的年龄或大小时使用 ILM 自动翻转数据流。  如果需要，您还可以手动翻转数据流。

#### Generation （代）

每个数据流跟踪它的生成：一个六位数的零填充整数，它充当流翻转的累积计数，从 000001 开始

创建后备索引时，索引使用以下约定命名

```
.ds-<data-stream>-<yyyy.MM.dd>-<generation>
```

<yyyy.MM.dd> 是后备索引的创建日期。  具有更高代的支持索引包含更新的数据。  例如，web-server-logs 
数据流有 34 代。该流的最新后备索引创建于 2099 年 3 月 7 日，名为 `.ds-web-server-logs-2099.03.07-000034`

#### 仅追加

数据流专为现有数据很少（如果有的话）更新的用例而设计。  您不能将现有文档的更新或删除请求直接发送到数据流。  相反，请使用按查询更新和按查询删除 API。

如果需要，您可以通过直接向文档的支持索引提交请求来更新或删除文档。

注：如果您经常更新或删除现有的时间序列数据，请使用带有写入索引的索引别名而不是数据流。  请[参阅管理没有数据流的时间序列数据](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/getting-started-index-lifecycle-management.html#manage-time-series-data-without-data-streams)。

#### 设置数据流

- 创建索引生命周期策略（可选）
- 创建组件模板
- 创建索引模板
- 创建数据流
- 保护数据流

您还可以将索引别名转换为数据流

**1. 创建索引生命周期策略**

虽然可选，但我们建议使用 ILM 自动管理数据流的支持索引。  ILM 需要索引生命周期策略

要在 Kibana 中创建索引生命周期策略，请打开主菜单并转到**Stack Management > Index Lifecycle Policies**.。  单击**Create policy**.。

您还可以使用创建生命周期策略 API 如下

```
PUT _ilm/policy/my-lifecycle-policy
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_primary_shard_size": "2mb"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "1d",
        "actions": {
          "forcemerge": {
            "max_num_segments": 1
          },
          "set_priority": {
            "priority": 50
          },
          "shrink": {
            "number_of_shards": 1
          }
        }
      },
      "cold": {
        "min_age": "2d",
        "actions": {
          "set_priority": {
            "priority": 0
          }
        }
      }
    }
  }
}
```

**2. 创建组件模板**

数据流需要匹配的索引模板。  在大多数情况下，您可以使用一个或多个组件模板来编写此索引模板。  您通常使用单独的组件模板进行映射和索引设置。  这使您可以在多个索引模板中重用组件模板

创建组件模板时，包括

- @timestamp 字段的`date`或 `date_nanos` 映射。  如果您不指定映射，Elasticsearch 会将 @timestamp 映射为具有默认选项的日期字段
- index.lifecycle.name 索引设置中的生命周期策略

要在 Kibana 中创建组件模板，请打开主菜单并转到 Stack Management > Index Management。  在索引模板视图中，单击创建组件模板

您还可以使用创建组件模板 API

```
PUT _component_template/my-mappings
{
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": {
          "format": "date_optional_time||epoch_millis",
          "type": "date"
        },
        "message": {
          "type": "wildcard"
        }
      }
    }
  },
  "_meta": {
    "description": "Mappings for @timestamp and message fields",
    "author": "wsm"
  }
}
# Creates a component template for index settings
PUT _component_template/my-settings
{
  "template": {
    "settings": {
      "index.lifecycle.name": "my-lifecycle-policy",
      "number_of_shards": 3,
      "number_of_replicas": 2
    }
  },
  "_meta": {
    "description": "Settings for ILM",
    "author": "wsm"
  }
}
```

**3. 创建索引模板**

- 一种或多种与数据流名称匹配的索引模式。  我们建议使用我们的数据流命名方案

  ```
  # type 描述数据的通用类型，例如日志、指标、跟踪或合成
  # dataset 数据集由集成定义，并描述了每个索引的摄取数据及其结构。
  # namespace 用户可配置的任意分组，例如环境（dev、prod 或 qa）、团队或战略业务单位
  <type>-<dataset>-<namespace>
  # 如 logs-nginx.access-prod  # 生成环境下nginx的access日志
  ```

- 该模板已启用数据流

- 包含您的映射和索引设置的任何组件模板

- 优先级高于 200 以避免与内置模板发生冲突。  请参阅避免索引模式冲突

要在 Kibana 中创建索引模板，或者API提交

```
PUT _index_template/my-index-template
{
  "priority": 500,
  "index_patterns": [
    "my-data-stream*"     # 索引模式
  ],
  "data_stream": {},  # 该模板创建数据流，而非索引
  "composed_of": [    # 指定组件模板
    "my-mappings",
    "my-settings"
  ],
  "_meta": {
    "description": "Template for my time series data",
    "author": "wsm"
  }
}
```

**4. 创建数据流**

索引请求将文档添加到数据流中。  这些请求必须使用`create`的 `op_type`。  文档必须包含 @timestamp 字段。

要自动创建数据流，请提交以流名称为目标的索引请求。  此名称必须与您的索引模板的索引模式之一匹配。

```
PUT my-data-stream/_bulk
{ "create":{ } }
{ "@timestamp": "2099-05-06T16:21:15.000Z", "message": "192.0.2.42 - - [06/May/2099:16:21:15 +0000] \"GET /images/bg.jpg HTTP/1.0\" 200 24736" }
{ "create":{ } }
{ "@timestamp": "2099-05-06T16:25:42.000Z", "message": "192.0.2.255 - - [06/May/2099:16:25:42 +0000] \"GET /favicon.ico HTTP/1.0\" 200 3638" }

POST my-data-stream/_doc
{
  "@timestamp": "2099-05-06T16:21:15.000Z",
  "message": "192.0.2.42 - - [06/May/2099:16:21:15 +0000] \"GET /images/bg.jpg HTTP/1.0\" 200 24736"
}
```

您还可以使用创建数据流 API 手动创建流。  流的名称仍必须与模板的索引模式之一匹配

```
PUT _data_stream/my-data-stream
```

**5. 保护数据流**

使用索引权限来控制对数据流的访问。  授予对数据流的权限会授予对其支持索引的相同权限

**6. 将索引别名转换为数据流**

在 Elasticsearch 7.9 之前，您通常会使用索引别名和写入索引来管理时间序列数据。  数据流取代了这一功能，需要较少的维护，并自动与数据层集成。

要将具有写入索引的索引别名转换为具有相同名称的数据流，请使用迁移到数据流 API。  在转换期间，别名的索引成为流的隐藏支持索引。  别名的写索引成为流的写索引。  该流仍然需要启用数据流的匹配索引模板

```
POST _data_stream/_migrate/my-time-series-data
```

**7. 获取有关数据流的信息**

```
GET _data_stream/my-data-stream
```

**8. 删除数据流**

```
DELETE _data_stream/my-data-stream
```

#### 使用数据流

**1. 将文档添加到数据流**

要添加单个文档，请使用索引 API

```
POST /my-data-stream/_doc/
{
  "@timestamp": "2099-03-08T11:06:07.000Z",
  "user": {
    "id": "8a4f500d"
  },
  "message": "Login successful"
}
```

您不能使用索引 API 的 `PUT /<target>/_doc/<_id>` 请求格式 将新文档添加到数据流。要指定文档 ID，请使用 `PUT /<target>/_create/<_id> `格式。  仅支持 create 的 op_type

要使用单个请求添加多个文档，请使用批量 API。  仅支持创建操作。

```
PUT /my-data-stream/_bulk?refresh
{"create":{ }}
{ "@timestamp": "2099-03-08T11:04:05.000Z", "user": { "id": "vlb44hny" }, "message": "Login attempt failed" }
{"create":{ }}
{ "@timestamp": "2099-03-08T11:06:07.000Z", "user": { "id": "8a4f500d" }, "message": "Login successful" }
{"create":{ }}
{ "@timestamp": "2099-03-09T11:07:08.000Z", "user": { "id": "l7gk7f82" }, "message": "Logout successful" }
```

**2. 搜索数据流**

获取数据流的统计信息

```
GET /_data_stream/my-data-stream/_stats?human=true
```

手动翻转数据流

```
POST /my-data-stream/_rollover/
```

开放关闭的后备索引

您无法搜索已关闭的后备索引，即使搜索其数据流也是如此。  您也不能更新或删除已关闭索引中的文档。

要重新打开已关闭的后备索引，请直接向索引提交开放索引 API 请求

```
POST /.ds-my-data-stream-2099.03.07-000001/_open/
```

要重新打开数据流的所有已关闭后备索引，请向流提交开放索引 API 请求

```
POST /my-data-stream/_open/
```

**3. 数据流重新索引(reindex)**

使用重新索引 API 将文档从现有索引、别名或数据流复制到数据流。  因为数据流是仅追加的，所以对数据流的重新索引必须使用 create 的 op_type。  重新索引无法更新数据流中的现有文档。

```
POST /_reindex
{
  "source": {
    "index": "archive"
  },
  "dest": {
    "index": "my-data-stream",
    "op_type": "create"
  }
}
```

**4. 通过查询更新数据流中的文档**

使用 `update by query API `更新数据流中与提供的查询匹配的文档：

```
POST /my-data-stream/_update_by_query
{
  "query": {
    "match": {
      "user.id": "l7gk7f82"
    }
  },
  "script": {
    "source": "ctx._source.user.id = params.new_id",
    "params": {
      "new_id": "XgdX0NoX"
    }
  }
}
```

**5. 通过查询删除数据流中的文档**

使用 `delete by query API` 删除数据流中与提供的查询匹配的文档

```
POST /my-data-stream/_delete_by_query
{
  "query": {
    "match": {
      "user.id": "XgdX0NoX"
    }
  }
}
```

**6. 更新或删除后备索引中的文档**

如果需要，您可以通过向包含文档的后备索引发送请求来更新或删除数据流中的文档。  你需要

- 文档 ID
- 包含文档的后备索引的名称
- 如果更新文档，它的序列号和主要术语

要获取此信息，请使用搜索请求

```
GET /my-data-stream/_search
{
  "seq_no_primary_term": true,
  "query": {
    "match": {
      "user.id": "yWIumJd7"
    }
  }
}
```

要更新文档，请使用带有有效 if_seq_no 和 if_primary_term 参数的索引 API 请求

```
PUT /.ds-my-data-stream-2022.06.10-000002/_doc/PvjaTIEBKZ_4nD7IqgPN?if_seq_no=2&if_primary_term=1
{
  "@timestamp": "2099-03-08T11:06:07.000Z",
  "user": {
    "id": "8a4f500d"
  },
  "message": "Login successful"
}
```

要删除文档，请使用删除 API

```
DELETE /.ds-my-data-stream-2022.06.10-000002/_doc/PvjaTIEBKZ_4nD7IqgPN
```

要使用单个请求删除或更新多个文档，请使用批量 API 的删除、索引和更新操作。  对于索引操作，包括有效的 if_seq_no 和 if_primary_term 参数

```
PUT /_bulk?refresh
{ "index": { "_index": ".ds-my-data-stream-2099.03.08-000003", "_id": "bfspvnIBr7VVZlfp2lqX", "if_seq_no": 0, "if_primary_term": 1 } }
{ "@timestamp": "2099-03-08T11:06:07.000Z", "user": { "id": "8a4f500d" }, "message": "Login successful" }
```

#### 更改数据流的映射和设置

每个数据流都有一个匹配的索引模板。  此模板中的映射和索引设置应用于为流创建的新后备索引。  这包括流的第一个后备索引，它是在创建流时自动生成的。

在创建数据流之前，我们建议您仔细考虑要包含在此模板中的映射和设置

如果您以后需要更改数据流的映射或设置，您有几个选择：

- 将新字段映射添加到数据流
- 更改数据流中的现有字段映射
- 更改数据流的动态索引设置
- 更改数据流的静态索引设置

如果您的更改包括对现有字段映射或静态索引设置的修改，则通常需要重新索引才能将更改应用于数据流的支持索引。  如果您已经在执行重新索引，则可以使用相同的过程来添加新的字段映射并更改动态索引设置。  请参阅使用重新索引更改映射或设置。

**1. 将新字段映射添加到数据流**

a.更新数据流使用的索引模板。  这可确保将新字段映射添加到为流创建的未来支持索引中.

以下创建或更新索引模板请求将新字段消息的映射添加到模板。

```
PUT /_index_template/my-data-stream-template
{
  "index_patterns": [ "my-data-stream*" ],
  "data_stream": { },
  "priority": 500,
  "template": {
    "mappings": {
      "properties": {
        "message": {        # 为新消息字段添加映射                         
          "type": "text"
        }
      }
    }
  }
}
```

b. 使用更新映射 API 将新字段映射添加到数据流。  默认情况下，这会将映射添加到流的现有后备索引，包括写入索引。

```
PUT /my-data-stream/_mapping
{
  "properties": {
    "message": {
      "type": "text"
    }
  }
}
```

要将映射仅添加到流的写入索引，请将更新映射 API 的 write_index_only 查询参数设置为 true

以下更新映射请求仅将新消息字段映射添加到 my-data-stream 的写入索引。  新字段映射不会添加到流的其他支持索引中

```
PUT /my-data-stream/_mapping?write_index_only=true
{
  "properties": {
    "message": {
      "type": "text"
    }
  }
}
```

**2. 更改数据流中的现有字段映射**

每个映射参数的文档说明您是否可以使用更新映射 API 为现有字段更新它。  要更新现有字段的这些参数，请执行以下步骤：

a. 更新数据流使用的索引模板。  这可确保将更新的字段映射添加到为流创建的未来支持索引中

以下创建或更新索引模板请求将 host.ip 字段的 ignore_malformed 映射参数的参数更改为 true

```
PUT /_index_template/my-data-stream-template
{
  "index_patterns": [ "my-data-stream*" ],
  "data_stream": { },
  "priority": 500,
  "template": {
    "mappings": {
      "properties": {
        "host": {
          "properties": {
            "ip": {
              "type": "ip",
              "ignore_malformed": true     # 更新        
            }
          }
        }
      }
    }
  }
}
```

b. 使用更新映射 API 将映射更改应用到数据流。  默认情况下，这会将更改应用于流的现有后备索引，包括写入索引。

```
PUT /my-data-stream/_mapping
{
  "properties": {
    "host": {
      "properties": {
        "ip": {
          "type": "ip",
          "ignore_malformed": true
        }
      }
    }
  }
}
```

要将映射更改仅应用于流的写入索引，请将 put 映射 API 的 `write_index_only` 查询参数设置为 true

除了支持的映射参数外，我们不建议您更改现有字段的映射或字段数据类型，即使在数据流的匹配索引模板或其支持索引中也是如此。  更改现有字段的映射可能会使任何已编入索引的数据无效

**3. 更改数据流的动态索引设置**

a. 更新数据流使用的索引模板。  这可确保将设置应用于为流创建的未来支持索引。

```
PUT /_index_template/my-data-stream-template
{
  "index_patterns": [ "my-data-stream*" ],
  "data_stream": { },
  "priority": 500,
  "template": {
    "settings": {
      "index.refresh_interval": "30s"   # index.refresh_interval 索引设置更改为 30s
    }
  }
}
```

b. 使用更新索引设置 API 来更新数据流的索引设置。  默认情况下，这会将设置应用于流的现有后备索引，包括写入索引。

```
PUT /my-data-stream/_settings
{
  "index": {
    "refresh_interval": "30s"
  }
}
```

要更改 `index.lifecycle.name` 设置，首先使用删除策略 API 删除现有的 ILM 策略。  请参阅切换生命周期策略。

**4. 更改数据流的静态索引设置**

静态索引设置只能在创建后备索引时设置。  您无法使用更新索引设置 API 更新静态索引设置

要将新的静态设置应用于未来的后备索引，请更新数据流使用的索引模板。  该设置会自动应用于更新后创建的任何后备索引。

```
PUT /_index_template/my-data-stream-template
{
  "index_patterns": [ "my-data-stream*" ],
  "data_stream": { },
  "priority": 500,
  "template": {
    "settings": {
      "sort.field": [ "@timestamp"],   # 增加          
      "sort.order": [ "desc"]          # 增加     
    }
  }
}
```

如果需要，您可以翻转数据流以立即将设置应用于数据流的写入索引。  这会影响翻转后添加到流中的任何新数据。  但是，它不会影响数据流的现有后备索引或现有数据

要将静态设置更改应用于现有的支持索引，您必须创建一个新的数据流并将您的数据重新索引到其中。  请参阅使用重新索引更改映射或设置

**5. 使用 reindex 更改映射或设置**

您可以使用重新索引来更改数据流的**映射或设置**。  这通常需要更改现有字段的**数据类型**或更新支持索引的**静态索引设置**。

要重新索引数据流，首先创建或更新索引模板，使其包含所需的映射或设置更改。  然后，您可以将现有数据流重新索引到与模板匹配的新流中。  这会将模板中的映射和设置更改应用于添加到新数据流中的每个文档和支持索引。  这些更改还会影响新流创建的任何未来支持索引。

1. 为新数据流选择名称或索引模式。  这个新的数据流将包含您现有流中的数据。

   您可以使用解析索引 API 检查名称或模式是否与任何现有索引、别名或数据流匹配。  如果是这样，您应该考虑使用其他名称或模式。

   以下解析索引 API 请求检查以 new-data-stream 开头的任何现有索引、别名或数据流是否存在。  如果不存在，则可以使用 new-data-stream* 索引模式来创建新的数据流。

   ```
   GET /_resolve/index/new-data-stream*
   # 返回以下响应，表示没有与此模式匹配的现有目标。
   {
     "indices": [ ],
     "aliases": [ ],
     "data_streams": [ ]
   }
   ```

2. 创建或更新索引模板。  此模板应包含您希望应用于新数据流的支持索引的映射和设置

   该索引模板必须满足数据流模板的要求。  它还应该包含您之前在 index_patterns 属性中选择的名称或索引模式。

   以下创建或更新索引模板 API 请求会创建一个新的索引模板 new-data-stream-template。  new-data-stream-template 以 my-data-stream-template 为基础，做了以下改动：

   - index_patterns 中的索引模式匹配任何以 new-data-stream 开头的索引或数据流
   - @timestamp 字段映射使用 date_nanos 字段数据类型而不是日期数据类型
   - 该模板包括 sort.field 和 sort.order 索引设置，这些设置不在原始 my-data-stream-template 模板中

   ```
   PUT /_index_template/new-data-stream-template
   {
     "index_patterns": [ "new-data-stream*" ],
     "data_stream": { },
     "priority": 500,
     "template": {
       "mappings": {
         "properties": {
           "@timestamp": {
             "type": "date_nanos"                 
           }
         }
       },
       "settings": {
         "sort.field": [ "@timestamp"],          
         "sort.order": [ "desc"]                 
       }
     }
   }
   ```

   

3. 使用创建数据流 API 手动创建新数据流。  数据流的名称必须与新模板的 index_patterns 属性中定义的索引模式匹配。

   我们不建议索引新数据来创建此数据流。  稍后，您会将现有数据流中的旧数据重新索引到这个新流中。  这可能会导致一个或多个包含新旧数据混合的后备索引。

   以下创建数据流 API 请求以 new-data-stream 为目标，它与 new-data-stream-template 的索引模式匹配。  因为没有现有的索引或数据流使用此名称，所以此请求会创建新数据流数据流。

   ```
   PUT /_data_stream/new-data-stream
   ```

   

4. 如果您不想在新数据流中混合新旧数据，请暂停索引新文档。  虽然混合新旧数据是安全的，但它可能会干扰数据保留。  请参阅在数据流中混合新旧数据。

5. 如果您使用 ILM 自动翻转，请减少 ILM 轮询间隔。  这确保了当前的写入索引在等待翻转检查时不会变得太大。  默认情况下，ILM 每 10 分钟检查一次翻转条件。

   以下集群更新设置 API 请求将 `indices.lifecycle.poll_interval` 设置降低到 1m（一分钟）

   ```
   PUT /_cluster/settings
   {
     "persistent": {
       "indices.lifecycle.poll_interval": "1m"
     }
   }
   ```

6. 使用 create 的 op_type 将数据重新索引到新数据流

   如果要按照最初索引的顺序对数据进行分区，可以运行单独的重新索引请求。  这些重新索引请求可以使用单独的后备索引作为源。  您可以使用获取数据流 API 来检索支持索引的列表。

   例如，您计划将 my-data-stream 中的数据重新索引到 new-data-stream。  但是，您希望为 my-data-stream 中的每个后备索引提交单独的重新索引请求，从最旧的后备索引开始。  这保留了数据最初索引的顺序。

   以下获取数据流 API 请求检索有关 my-data-stream 的信息，包括其支持索引的列表

   ```
   GET /_data_stream/my-data-stream
   ```

   响应的 indices 属性包含流的当前支持索引的数组。  数组中的第一项包含有关流的最旧后备索引的信息。

   以下重新索引 API 请求将文档从 `.ds-my-data-stream-2099.03.07-000001` 复制到 `new-data-stream`。  请求的 op_type 是 create

   ```
   POST /_reindex
   {
     "source": {
       "index": ".ds-my-data-stream-2099.03.07-000001"
     },
     "dest": {
       "index": "new-data-stream",
       "op_type": "create"
     }
   }
   ```

   您还可以使用查询为每个请求仅重新索引文档子集。

   以下重新索引 API 请求将文档从 my-data-stream 复制到 new-data-stream。  该请求使用范围查询仅重新索引具有上周内时间戳的文档。  注意请求的 op_type 是 create。

   ```
   POST /_reindex
   {
     "source": {
       "index": "my-data-stream",
       "query": {
         "range": {
           "@timestamp": {
             "gte": "now-7d/d",
             "lte": "now/d"
           }
         }
       }
     },
     "dest": {
       "index": "new-data-stream",
       "op_type": "create"
     }
   }
   ```

7. 如果您之前更改了 ILM 轮询间隔，请在重新索引完成后将其更改回其原始值。  这可以防止主节点上不必要的负载。

   以下集群更新设置 API 请求将 indices.lifecycle.poll_interval 设置重置为其默认值

   ```
   PUT /_cluster/settings
   {
     "persistent": {
       "indices.lifecycle.poll_interval": null
     }
   }
   ```

8. 使用新数据流恢复索引。  对此流的搜索现在将查询您的新数据和重新索引的数据

9. 一旦您确认所有重新索引的数据在新数据流中都可用，您就可以安全地删除旧数据流

10. 以下删除数据流 API 请求将删除 my-data-stream。  此请求还会删除流的支持索引及其包含的任何数据。

    ```
    DELETE /_data_stream/my-data-stream
    ```

    

