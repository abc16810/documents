#### 创建索引

新建 Index，可以直接向 ES 服务器发出 `PUT` 请求

```
curl  -X PUT http://localhost:9200/customer?pretty   # 创建一个默认的customer 索引
PUT /test     # 创建一个索引test 3个分片，2个副本
{
  "settings": {
    "index": {
      "number_of_shards": 3,
      "number_of_replicas": 2
    }
  }
}
```

#### 删除索引

```
# DELETE 请求删除索引
# curl -X DELETE http://localhost:9200/test
{"acknowledged":true}
# 删除多个索引
DELETE /index_one,index_two
DELETE /index_*
```

#### 查看索引

```
curl  http://localhost:9200/test?pretty
curl  http://localhost:9200/test/_count?pretty   # test文档个数
curl  http://localhost:9200/test/_search?pretty  #查看test索引前10条文档

curl  http://localhost:9200/_cat/indices/test*?v  # 查看test的indices
curl  http://localhost:9200/_cat/indices?health=green  # 查看状态为绿的索引
# 按照文档个数排序
curl  http://localhost:9200/_cat/indices?v&s=docs.count:desc
# 查看索引占用的空间内存
curl  http://localhost:9200/_cat/indices?v&h=i,tm&s=tm:desc
```

#### 索引别名

ES 的索引别名就是给一个索引或者多个索引起的另一个名字，典型的应用场景是针对索引使用的平滑切换

```
PUT /test/_alias/my_test
POST /_aliases
{
  "actions": [
    { "add": { "index": "test", "alias": "my_test" }}
  ]
}
```

也可以在一次请求中增加别名和移除别名混合使用

```
POST /_aliases
{
  "actions": [
    { "remove": { "index": "test", "alias": "my_test" }}
    { "add": { "index": "test_v2", "alias": "my_test_v2" }}
  ]
}
```

#### 文档

```
# put 更新文档，如果相应id文档存在，则更新（先删除，在写入） 否则创建
curl -H "Content-Type: application/json" -XPUT http://localhost:9200/test/_doc/1?pretty -d  '{ "name":"wsm"}'
# post 创建文档不指定ID 自动生成 _id
curl -H "Content-Type: application/json" -XPOST http://localhost:9200/test/_doc?pretty -d  '{ "name":"wsm_2"}'
# create document. 指定Id。如果id已经存在，报错
PUT users/_doc/1?op_type=create
#create document. 指定 ID 如果已经存在，就报错
PUT users/_create/1
# 查看文档
GET users/_doc/1
# 返回的数据中，found 字段表示查询成功，_source 字段返回原始记录
# 查询所有记录
GET test/_doc/_search?pretty
# 上面代码中，返回结果的 took字段表示该操作的耗时（单位为毫秒），timed_out字段表示是否超时，hits字段表示命中的记录，里面子字段的含义如下。
#    total：返回记录数，本例是 2 条。
#    max_score：最高的匹配程度，本例是1.0。
#    hits：返回的记录组成的数组。返回的记录中，每条记录都有一个_score字段，表示匹配的程序，默认是按照这个字段降序排列

# 更新文档 （更新的时候也可以添加的新的字段）
POST test/_doc/1/_update?pretty
# 删除文档
DELETE users/_doc/1
```

**批量操作**

```
curl -H "Content-Type: application/json" -XPOST http://localhost:9200/test/_doc/_bulk?pretty --data-binary @/tmp/data
# cat /tmp/data
{"update":{"_id":"1"}}
{"doc": { "name": "John Doe becomes Jane Does"} }

POST _bulk
{ "index" : { "_index" : "test", "_id" : "1" } }
{ "field1" : "value1" }
{ "delete" : { "_index" : "test", "_id" : "2" } }
{ "create" : { "_index" : "test2", "_id" : "3" } }
{ "field1" : "value3" }
{ "update" : {"_id" : "1", "_index" : "test"} }
{ "doc" : {"field2" : "value2"} }
```

#### 全文搜索

一种传统数据库很难实现的功能。我们将会搜索所有name字段包含`wsm`的文档

```
curl -H 'Content-Type: application/json' 'localhost:9200/test/_doc/_search?pretty'  -d '{         
"query" : { "match" : { "name" : "wsm" }}
}'
# 或者-XPOST  请求
```

默认情况下，Elasticsearch根据结果相关性评分来对结果集进行排序，所谓的「结果相关性评分」就是文档与查询条件的匹配程度。elasticsearch在各种文本字段中进行全文搜索，并且返回相关性最大的结果集。**相关性(relevance)**的概念在Elasticsearch中非常重要，而这个概念在传统关系型数据库中是不可想象的，因为传统数据库对记录的查询只有匹配或者不匹配。

Elastic 默认一次返回 10 条结果，可以通过`size`字段改变这个设置，还可以通过`from`字段，指定位移

```
{
  "query" : { "match" : { "desc" : "管理" }},
  "from": 1,
  "size": 1
}'
# 上面代码指定，从位置 1 开始（默认是从位置 0 开始），只返回一条结果

# 执行match_all并返回文档10到19:
GET /test/_search
{
  "query": { "match_all": {} },
  "from": 10,
  "size": 10
}
```

如果有多个搜索关键字， Elastic 认为它们是`or`关系

```
{
"query" : { "match" : { "name" : "aaa wsm" }}
}'
```

如果要执行多个关键词的`and`搜索，必须使用**BOOL query**  (must 必须都为True, should有一个为True即可,must_not  都不包含)

```
{
  "query": {
    "bool": {
      "must": [
        { "match": { "name": "wsm" } },
        { "match": { "name": "aaa" } }
      ]
    }
  }
}
```

#### URI Search查询语义(query string)

因为我们像传递URL参数一样去传递查询语句

````
curl http://localhost:9200/test/_doc/_search?q=name:wsm    # Term 查询
# 搜索test索引里的所有文档 age升序排序
curl http://localhost:9200/test/_search?q=*&sort=age:asc&pretty
# 如下查询方法和上述的相同
GET /test/_search
{
  "query": { "match_all": {} },
  "sort": [
    { "age": "asc" }
  ]
}

curl -H "Content-Type: application/json" -XGET http://localhost:9200/test/_search?q=2012&df=name&sort=year:desc&from=0&size=10&timeout=1s -d '{"profile": true}'
# q 指定查询语句，使用 QueryString 语义
# df 字段，不指定时所有字段
# sort 排序：from 和 size 用于分页
# profile 可以查看查询时如何被执行的

# Boolean 查询
GET /test/_search?q=name:aa bb   # 等效于 aa OR bb

# 使用引号，Phrase（短语）查询
GET /test/_search?q=title:"aa bb"  等效于 aa AND bb

# 多个索引下匹配
GET /my-index1,my-index2/_search?q=name:wsm
# 所有索引下匹配
GET _all/_search?q=name:wsm
````

**AND、OR、NOT 或者 &&、||、!**

```
# 布尔操作符
GET /test/_search?q=name:(wsm AND aa)  # AND 必须大写
GET /test/_search?q=name:(wsm NOT aa)
```

**范围查询**

- `[]` 表示闭区间
- `{}` 表示开区间

```
# 范围查询 ,区间写法
GET /test/_search?q=name:wsm AND year:{2010 TO 2018}
GET /test/_search?q=name:wsm AND year:[* TO 2018]
```

**算数符**

```
# 2010 年以后的记录
GET /test/_search?q=year:>2010
# 2010 年到 2018 年的记录
GET /test/_search?q=year:(>2010 && <=2018)
# 2010 年到 2018 年的记录
GET /test/_search?q=year:(+>2010 +<=2018)
```

**通配符查询**

```
GET /test/_search?q=name:ws?   #? 代表 1 个字符
GET /test/_search?q=name:ws*   # *代表 0 或多个字符
```

**模糊匹配**

在查询文本或关键字字段时，模糊性被解释为Levenshtein编辑距离——需要对一个字符串进行一个字符更改的数量，以使其与另一个字符串相同

```
# # 相似度在 1 个字符以内
GET /test/_search?q=name:aaad~1
# 相似度在 2 个字符以内
GET /test/_search?q=name:"wsm 00"~2
```

#### 响应过滤

所有REST api都接受一个filter_path参数，该参数可用于减少Elasticsearch返回的响应。

这个参数采用逗号分隔的过滤器列表，用点符号表示:

```
test/_search?q=wsm&filter_path=took,hits.hits._id,hits.hits._score
# 它还支持*通配符匹配任何字段或字段名的一部分
curl -X GET "localhost:9200/_cluster/state?filter_path=metadata.indices.*.stat*"
# 并且，**通配符可以用来包含字段，而不需要知道字段的确切路径。
curl -X GET "localhost:9200/_cluster/state?filter_path=routing_table.indices.**.state"
```

#### URI 中允许的参数

| 名称                          | 描述                                                         |
| ----------------------------- | ------------------------------------------------------------ |
| q                             | 查询字符串，映射到 query_string 查询                         |
| df                            | 在查询中未定义字段前缀时使用的默认字段                       |
| analyzer                      | 查询字符串时指定的分词器                                     |
| analyze_wildcard              | 是否允许通配符和前缀查询，默认设置为 false                   |
| batched_reduce_size           | 应在协调节点上一次减少的分片结果数。如果请求中潜在的分片数量很大，则应将此值用作保护机制，以减少每个搜索请求的内存开销， 默认512 |
| default_operator              | 默认使用的匹配运算符，可以是*AND*或者*OR*，默认是*OR*        |
| max_concurrent_shard_requests | 定义每个节点并发执行的shard请求数。这个值应该用来限制搜索对集群的影响，以限制并发的shard请求的数量 默认5 |
| preference                    | 指定用于搜索的节点和分片。 默认情况下，Elasticsearch使用自适应副本选择从符合条件的节点和shard中进行选择，考虑到分配感知。 |
| lenient                       | 如果设置为 true，将会忽略由于格式化引起的问题（如向数据字段提供文本），默认为 false |
| explain                       | 对于每个 hit，包含了具体如何计算得分的解释                   |
| _source                       | 请求文档内容的参数，默认 true；设置 false 的话，不返回_source 字段，可以使用source_include和_source_exclude参数分别指定返回字段和不返回的字段 |
| stored_fields                 | 指定每个匹配返回的文档中的存储字段，多个用逗号分隔。不指定任何值将导致没有字段返回 |
| sort                          | 排序方式，可以是*fieldName*、*fieldName:asc*或者*fieldName:desc*的形式。fieldName 可以是文档中的实际字段，也可以是诸如_score 字段，其表示基于分数的排序。此外可以指定多个 sort 参数（顺序很重要） |
| track_scores                  | 如果为真，则计算并返回文档分数，即使这些分数不用于排序。默认值为false |
| track_total_hits              | 是否返回匹配条件命中的总文档数，如果为真，则以性能为代价返回准确的命中数。 如果为false，则响应不包括匹配查询的总命中数。 默认10000 |
| timeout                       | 设置搜索的超时时间，默认无超时时间                           |
| terminate_after               | 在达到查询终止条件之前，指定每个分片收集的最大文档数。如果设置，则在响应中多了一个 terminated_early 的布尔字段，以指示查询执行是否实际上已终止。默认为 no terminate_after |
| from                          | 从第几条（索引以 0 开始）结果开始返回，默认为 0              |
| size                          | 返回命中的文档数，默认为 10。默认情况下，使用from和size参数不能浏览超过10000条数据， 可以使用search_after参数 |
| search_type                   | 搜索的方式，可以是*dfs_query_then_fetch*或*query_then_fetch*。默认为*query_then_fetch* |
| allow_partial_search_results  | 是否可以返回部分结果。如设置为 false，表示如果请求产生部分结果，则设置为返回整体故障；默认为 true，表示允许请求在超时或部分失败的情况下获得部分结果 |
| timeout                       | 指定等待每个分片响应的时间间隔。如果在超时时间内没有收到响应，则请求失败并返回一个错误。默认为无超时 |

#### DSL（Domain Specific Language）

我们依旧想要找到name为“wsm”的员工，但是我们只想得到年龄大于30岁的员工。我们的语句将添加**过滤器(filter)**,它使得我们高效率的执行一个结构化搜索

```
# es 5.0版本更新后，filtered的查询将替换为bool查询。 filtered是比较老的的版本的语法。现在目前已经被bool替代。推荐使用bool
{
  "query": {
    "bool": {
      "must": {
        "match": {
          "name": "wsm"
        }
      },
      "filter": {
        "range": {
          "sex": {
            "gt": 0
          }
        }
      }
    }
  }
}
```

返回指定字段`_source 过滤`。如果 `_source` 没有存储，那就只返回匹配的文档的元数据

```
_source` 支持使用通配符，如：`_source["name*", "desc*"]
GET /test/_search
{
  "query": { "match_all": {} },
  "_source": ["name", "sex"]
}  类似于sql 的 select name，sex from table; 
```

`ignore_unavailable`  这包括不存在的索引或关闭的索引。可以指定true或false

```
GET /test2/_search?ignore_unavailable=true   # 如果索引不存在，返回空 
```

 指定操作符

```
GET /test/_search
{
  "query": {
    "match": {
      "name": {
        "query": "wsm tomcat",
        "operator": "and"   
      }
    }
  }
}
```

**排序**

最好在数字型或日期型字段上排序。因为对于多值类型或分析过的字段排序，系统会选一个值，无法得知该值

```
GET /test/_search
{
  "query": { "match_all": {} },
  "sort": [
    { "age": "asc" }
  ]
}
```

#### 短语搜索

目前我们可以在字段中搜索单独的一个词，这挺好的，但是有时候你想要确切的匹配若干个单词或者**短语(phrases)**。例如我们想要查询同时包含"rock"和"climbing"（并且是相邻的）的员工记录。 要做到这个，我们只要将match查询变更为match_phrase查询即可:

```
{
  "query": {
    "match_phrase": {
      "name": {
        "query": "rock climbing"
      }
    }
  }
}
```

#### 高亮我们的搜索

很多应用喜欢从每个搜索结果中**高亮(highlight)**匹配到的关键字，这样用户可以知道为什么这些文档和查询相匹配。在Elasticsearch中高亮片段是非常容易的。

让我们在之前的语句上增加highlight参数

```
{
  "query": {
    "match_phrase": {
      "name": {
        "query": "wsm 222"
      }
    }
  },
  "highlight": {
    "fields": {
      "name": {}
    }
  }
}
```

#### 聚合

Elasticsearch有一个功能叫做**聚合(aggregations)**，它允许你在数据上生成复杂的分析统计。它很像SQL中的GROUP BY但是功能更强大

```
{
  "aggs": {
    "all_interests": {
      "terms": {
        "field": "age"
      }
    }
  }
}
```

先匹配再聚合，聚合也允许分级汇总等

```
{
  "query": {
    "match": {
      "last_name": "Smith"
    }
  },
  "aggs": {
    "all_interests": {
      "terms": {
        "field": "age"
      }
    }
  }
}
# 分级汇总。例如，让我们统计每种兴趣下职员的平均年龄
{
  "aggs": {
    "all_interests": {
      "terms": {
        "field": "interests"
      },
      "aggs": {
        "avg_age": {
          "avg": {
            "field": "age"
          }
        }
      }
    }
  }
}
```

**term**

term是代表完全匹配，即不进行分词器分析，文档中必须包含整个搜索的词汇

```
{
  "query": {
    "term" : { "user" : "Kimchy" }
  }
}
# Finds documents which contain the exact term 'Kimchy' in the inverted index of the user field.
```

#### 集群 API

```
# 如果没有给出过滤器，默认是查询所有节点
GET /_nodes
# 查询所有节点
GET /_nodes/_all
# 查询本地节点
GET /_nodes/_local
# 查询主节点
GET /_nodes/_master
# 根据名称查询节点（支持通配符）
GET /_nodes/node_name_goes_here
GET /_nodes/node_name_goes_*
# 根据地址查询节点（支持通配符）
GET /_nodes/10.0.0.3,10.0.0.4
GET /_nodes/10.0.0.*
# 根据规则查询节点
GET /_nodes/_all,master:false
GET /_nodes/data:true,ingest:true
GET /_nodes/coordinating_only:true
GET /_nodes/master:true,voting_only:false
# 根据自定义属性查询节点（如：查询配置文件中含 node.attr.rack:2 属性的节点）
GET /_nodes/rack:2
GET /_nodes/ra*:2
GET /_nodes/ra*:2*
```

**集群健康 API**

```
GET /_cluster/health
GET /_cluster/health?level=shards
GET /_cluster/health/kibana_sample_data_flights?level=shards
# 集群状态 API 返回表示整个集群状态的元数据
GET /_cluster/state
```

**节点 API**

```
# curl -X GET "localhost:9200/_cat/nodes?v=true"
# curl -X GET "localhost:9200/_cat/nodes?v=true&h=id,ip,port,v,m"
id   ip            port v      m
P3zV 192.168.192.2 9300 7.17.1 *
EDqg 192.168.192.3 9300 7.17.1 -
JTgu 192.168.192.4 9300 7.17.1 -
```

**分片 API** shards 命令是哪些节点包含哪些分片的详细视图。它会告诉你它是主还是副本、文档数量、它在磁盘上占用的字节数以及它所在的节点

````
# 查看默认的字段 所有索引的分片信息
# curl -X GET "localhost:9200/_cat/shards"
# 根据名称查询分片（支持通配符）
# curl -X GET "localhost:9200/_cat/shards/tes*"
# 查看指定的字段
# curl -X GET "localhost:9200/_cat/shards?h=index,shard,prirep,state,unassigned.reason"
````

**监控 API**

Elasticsearch 中集群相关的健康、统计等相关的信息都是围绕着 `cat` API 进行的

```
GET /_cat

/_cat/allocation       # 资产使用情况
/_cat/shards
/_cat/shards/{index}
/_cat/master
/_cat/nodes
/_cat/tasks
/_cat/indices
/_cat/indices/{index}
/_cat/segments
/_cat/segments/{index}
/_cat/count
/_cat/count/{index}
/_cat/recovery
/_cat/recovery/{index}
/_cat/health
/_cat/pending_tasks
/_cat/aliases
/_cat/aliases/{alias}
/_cat/thread_pool
/_cat/thread_pool/{thread_pools}
/_cat/plugins
/_cat/fielddata
/_cat/fielddata/{fields}
/_cat/nodeattrs
/_cat/repositories
/_cat/snapshots/{repository}
/_cat/templates
```

#### 常见的选项

- ?pretty=true   返回友好的json
- ?format=yaml
- ?human=false   默认 关闭可读性
- v=true

