#### Mapping 

在 Elasticsearch 中，**Mapping**（映射），用来定义一个文档以及其所包含的字段如何被存储和索引，可以在映射中事先定义字段的数据类型、字段的权重、分词器等属性，就如同在关系型数据库中创建数据表时会设置字段的类型

string类型在ElasticSearch 旧版本中使用较多，从ElasticSearch 5.x开始不再支持string，由text和keyword类型替代。7.0 开始，不需要在 Mapping 定义中指定 type 信息

映射是定义如何存储和索引文档及其包含的字段的过程。例如，使用映射来定义

1、应该将哪些字符串字段视为全文字段

2、哪些字段包含数字、日期或地理位置

3、文档中所有字段的值是否应该索引到catch-all _all字段

4、日期格式化

5、用于控制映射的自定义规则 [dynamically added fields](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/dynamic-mapping.html).

**Mapping 类型**

1、元字段用于自定义如何处理与文档关联的元数据。元字段的例子包括文档的_index、_type、_id和_source字段

2、映射类型包含与文档相关的字段或属性列表。

字段数据类型

- 一个简单的类型  [text](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/text.html), [keyword](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/keyword.html), [date](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/date.html), [long](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/number.html), [double](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/number.html), [boolean](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/boolean.html) or [ip](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/ip.html)
- 一种支持JSON层次结构的类型，例如[object](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/object.html) or [nested](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/nested.html).
- 或者一种专门的类型 [geo_point](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/geo-point.html), [geo_shape](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/geo-shape.html), or [completion](https://www.elastic.co/guide/en/elasticsearch/reference/6.4/search-suggesters-completion.html).

#### 映射分类

在 Elasticsearch  中，映射可分为静态映射和动态映射。在关系型数据库中写入数据之前首先要建表，在建表语句中声明字段的属性，在 Elasticsearch  中，则不必如此，Elasticsearch 最重要的功能之一就是让你尽可能快地开始探索数据，文档写入 Elasticsearch  中，它会根据字段的类型自动识别，这种机制称为**动态映射**，而**静态映射**（**显式映射**）则是写入数据之前对字段的属性进行手工设置

如何定义一个显式映射 Mapping

```
PUT /books
{
  "mappings": {
    "properties": {
      "age":    { "type": "integer" },  
      "email":  { "type": "keyword"  }, 
      "name":   { "type": "text"  }     
    }
  }
}
# 向现有映射添加字段
PUT /my-index-000001/_mapping
{
  "properties": {
    "employee-id": {
      "type": "keyword",
      "index": false  # 索引选项控制字段值是否被索引。它接受true或false，默认值为true。没有索引的字段是不可查询的。
    }
  }
}
# 查看指定字段的映射
GET /my-index-000001/_mapping/field/employee-id
```

**动态映射**是一种偷懒的方式，可直接创建索引并写入文档，文档中字段的类型是 Elasticsearch **自动识别**的，不需要在创建索引的时候设置字段的类型。在实际项目中，如果遇到的业务在导入数据之前不确定有哪些字段，也不清楚字段的类型是什么，使用动态映射非常合适。当
Elasticsearch 
在文档中碰到一个以前没见过的字段时，它会利用动态映射来决定该字段的类型，并自动把该字段添加到映射中，根据字段的取值自动推测字段类型的规则见下表：

| JSON 格式的数据 | 自动推测的字段类型                                           |
| --------------- | ------------------------------------------------------------ |
| null            | 没有字段被添加                                               |
| true or false   | boolean 类型                                                 |
| 浮点类型数字    | float 类型                                                   |
| 数字            | long 类型                                                    |
| JSON 对象       | object 类型                                                  |
| 数组            | 由数组中第一个非空值决定                                     |
| string          | 有可能是 date 类型（若开启日期检测）、double 或 long 类型、text 类型、keyword 类型 |

使用动态 mapping 要结合实际业务需求来综合考虑，如果将 Elasticsearch 当作主要的数据存储使用，并且希望出现未知字段时抛出异常来提醒你注意这一问题，那么开启动态 mapping 并不适用。在 mapping 中可以通过 `dynamic` 设置来控制是否自动新增字段，接受以下参数

- **true**：默认值为 true，自动添加字段。
- **false**：忽略新的字段。
- **strict**：严格模式，发现新的字段抛出异常。
- runtime  新字段作为运行时字段添加到映射中。这些字段没有索引，并且在查询时从_source加载

```
# 在类型级别禁用了动态映射，因此不会动态添加新的顶级字段, 如果嵌套字段开启了动态映射，那么对象支持动态映射，因此您可以向这个内部对象添加字段
{
  "mappings": {
    "dynamic": false
    }
 }
```

您可以自定义用于日期检测和数字检测的动态字段映射规则。要定义可应用于其他动态字段的自定义映射规则，请使用dynamic_templates。

- `date_detection` 如果启用了date_detection(默认值)，则会检查新的字符串字段，以查看它们的内容是否匹配dynamic_date_formats中指定的任何日期模式。如果找到匹配项，则添加一个新的日期字段，该字段具有相应的格式 [ [`"strict_date_optional_time"`](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/mapping-date-format.html#strict-date-time),`"yyyy/MM/dd HH:mm:ss Z||yyyy/MM/dd Z"`]

  ```
  # 可以通过将date_detection设置为false来禁用动态日期检测, 字段解析为text字段
  date_detection
  {
    "mappings": {
      "date_detection": false
    }
  }
  # 自定义dynamic_date_formats支持你自己的日期格式
  PUT my-index-000001
  {
    "mappings": {
      "dynamic_date_formats": ["MM/dd/yyyy"]
    }
  }
  ```

- `numeric_detection`虽然JSON支持本地浮点和整数数据类型，但有些应用程序或语言有时可能将数字呈现为字符串。通常正确的解决方案是显式地映射这些字段，但数字检测(默认禁用)可以启用自动执行此操作:

  ```
  {
    "mappings": {
      "numeric_detection": true
    }
  }
  ```

**更新现有字段映射**

除了文档化的地方，现有的字段映射不能更新。更改映射将意味着已经索引的文档无效。相反，您应该创建一个具有正确映射的新索引，并将数据重新索引到该索引。如果只希望重命名字段而不更改其映射，引入别名字段可能是有意义的

```
# 使用更新的映射API为现有的user_identifier字段添加user_id字段别名
PUT /my-index-000001/_mapping
{
  "properties": {
    "user_id": {
      "type": "alias",
      "path": "user_identifier"
    }
  }
}
```

#### Mapping 属性

| 属性名          | 描述                                                         |
| :-------------- | :----------------------------------------------------------- |
| properties      | 类型映射、对象字段和嵌套字段包含子字段被称为`properties`     |
| type            | 字段类型，常用的有 text、integer 等等。                      |
| index           | 当前字段是否被作为索引。可选值为 true，默认为 true。         |
| boost           | 在查询时间，单个字段可以被自动提升——计算更多的相关度得分, 应用于`term queries` |
| coerce          | 强制试图清除脏值以适合字段的数据类型,字符串将被强制转换为数字,浮点数将被整数值截断, 默认启用强制转换 |
| doc_values      | 所有支持文档值的字段默认启用它们。如果你确定你不需要对一个字段排序或聚合，或者从脚本中访问字段值，你可以禁用doc值以节省磁盘空间 |
| store           | 是否存储指定字段，设置 true 意味着需要开辟单独的存储空间为这个字段做存储，而且这个存储是独立于 _source 的存储的 |
| enabled         | 启用的设置只能应用于顶级映射定义和对象字段，这会导致Elasticsearch完全跳过对字段内容的解析。JSON仍然可以从_source字段中检索，但不能以任何其他方式搜索或存储。整个映射也可能被禁用 |
| format          | 自定义时间格式化`"format": "yyyy-MM-dd"`                     |
| ignore_above    | 超过`ignore_above`的字符串将不会被索引或存储。对于字符串数组，ignore_above将分别应用于每个数组元素，比ignore_above长的字符串元素将不会被索引或存储 |
| norms           | 是否使用归一化因子，不需要对某字段进行打分排序时，可禁用它，节省空间；*type* 为 *text* 时，默认为 *true*；而 *type* 为 *keyword* 时，默认为 *false*。 |
| index_options   | 索引选项控制添加到倒排索引（Inverted Index）的信息，这些信息用于搜索（Search）和高亮显示。只使用文本字段。docs：只索引文档编号(Doc Number)；freqs：索引文档编号和词频率（term frequency）；positions：索引文档编号，词频率和词位置（序号）；offsets：索引文档编号，词频率，词偏移量（开始和结束位置）和词位置（序号）。默认情况下，被分析的字符串（analyzed string）字段使用 *positions*，其他字段默认使用 *docs*。此外，需要注意的是 *index_option* 是 elasticsearch 特有的设置属性；临近搜索和短语查询时，*index_option* 必须设置为 *offsets*，同时高亮也可使用 postings highlighter |
| index_prefixes  | index_prefixes参数允许对词汇前缀进行索引，以加速前缀搜索 `min_chars` 必须大于0 默认2 。`max_chars` 必须小于20 默认5 |
| term_vector     | 索引选项控制词向量相关信息：no：默认值，表示不存储词向量相关信息；yes：只存储词向量信息；with_positions：存储词项和词项位置；with_offsets：存储词项和字符偏移位置；with_positions_offsets：存储词项、词项位置、字符偏移位置。*term_vector* 是 lucene 层面的索引设置。 |
| similarity      | 指定文档相似度算法（也可以叫评分模型）：**BM25**：ES5 之后的默认设置 |
| copy_to         | 复制到自定义 _all 字段，值是数组形式，即表明可以指定多个自定义的字段 |
| search_analyzer | 指定搜索时的分析器，搜索时的优先级最高                       |
| null_value      | 用于需要对 Null 值实现搜索的场景，只有 Keyword 类型支持此配置 |
| analyzer        | 分析器参数指定索引或搜索文本字段时用于文本分析的分析器。这个分析器将同时用于索引和搜索分析，如果指定search_analyzer，覆盖搜索分线器 |

#### 映射爆炸

在索引中定义太多字段可能导致映射爆炸，从而导致内存错误和难以恢复的情况。这个问题可能比预期的更普遍。例如，考虑这样一种情况，插入的每个新文档都会引入新的字段，这在动态映射中很常见

每当文档中包含新字段时，这些字段将最终出现在索引的映射中。对于少量数据来说，这并不令人担心，但随着映射的增长，这可能成为一个问题。以下设置允许您限制可以手动或动态创建的字段映射的数量，以防止糟糕的文档导致映射爆炸

`index.mapping.total_fields.limit`   索引中的最大字段数 默认1000

`index.mapping.depth.limit` 场的最大深度，用内部物体的数量来衡量。例如，如果所有字段都在根对象级别定义，那么深度为1。如果有一个对象映射，那么深度是2，等等。默认值是20

`index.mapping.nested_fields.limit`  索引中不同嵌套映射的最大数目。嵌套类型只应在特殊情况下使用，即需要相互独立地查询对象数组。为了防止设计不良的映射，该设置限制了每个索引唯一嵌套类型的数量。默认是50

`index.mapping.nested_objects.limit` 单个文档可以包含所有嵌套类型的嵌套JSON对象的最大数量。当文档包含太多嵌套对象时，此限制有助于防止内存不足错误。默认是10000

