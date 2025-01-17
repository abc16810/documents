### beats
    Filebeat
    Metricbeat
    Heartbeat
    Auditbeat
    Packetbeat
    Journalbeat

#### container inputs
使用容器输入读取容器日志文件。
该输入搜索给定路径下的容器日志，并将它们解析为公共消息行，同时提取时间戳。一切都发生在行过滤、多行和JSON解码之前，所以这个输入可以与这些设置结合使用。
```
filebeat.inputs:
- type: container
  paths: 
    - '/var/log/containers/*.log'
```
**配置选项**

- stream: 只从指定的流中读取:all, stdout或stderr。默认为all。
- format: 读取日志文件时使用给定的格式:auto、docker或cri。默认为auto，它将自动检测格式。若要禁用自动检测，请设置任何其他选项。

下面的输入配置Filebeat从默认Kubernetes日志路径下的所有容器读取标准输出流:
```
- type: container
  stream: stdout
  paths:
    - "/var/log/containers/*.log"
```
- encoding: 用于读取包含国际字符的数据的文件编码 `plain`编码是特殊的，因为它不验证或转换任何输入。
- exclude_lines: 正则表达式列表，用于匹配希望Filebeat排除的行。Filebeat删除列表中与正则表达式匹配的任何行。默认情况下，不删除任何行。空行将被忽略
如果还指定了多行设置，则在exclude_lines对行进行筛选之前，将每条多行消息组合成一行。
下面的示例将Filebeat配置为删除以DBG开头的任何行。
```
filebeat.inputs:
- type: container
  ...
  exclude_lines: ['^DBG']
```
- include_lines: 正则表达式列表，用于匹配您希望Filebeat包含的行。Filebeat仅导出列表中与正则表达式匹配的行。缺省情况下，导出所有行。空行将被忽略。
如果还指定了多行设置，则在include_lines对行进行筛选之前，将每条多行消息组合成一行。
下面的示例配置Filebeat导出任何以ERR或WARN开头的行:
```
filebeat.inputs:
- type: container
  ...
  include_lines: ['^ERR', '^WARN']
```
- harvester_buffer_size: 每个harvester在获取文件时使用的缓冲区的字节大小。默认值是16384。
- max-bytes: 单个日志消息所能具有的最大字节数。max_bytes之后的所有字节将被丢弃，不发送。这个设置对于多行日志消息特别有用，因为多行日志消息可能很大。默认值是10MB(10485760)。
- json: 这些选项使Filebeat能够解码JSON消息结构的日志。Filebeat逐行处理日志，因此只有当每行有一个JSON对象时，JSON解码才有效。

解码发生在行滤波和多行之前。如果设置message_key选项，可以将JSON解码与过滤和多行结合起来。这在应用程序日志被包装在JSON对象中的情况下很有帮助，例如在Docker中就会发生这种情况。
```
json.keys_under_root: true
json.add_error_key: true
json.message_key: log
```
您必须指定以下至少一个设置来启用JSON解析模式:
- ` keys_under_root`: 默认情况下，解码后的JSON放在输出文档中的“JSON”键下。如果启用此设置，键将在输出文档的顶层复制。默认为false。
- `overwrite_keys`: 如果启用了keys_under_root和此设置，则来自解码后的JSON对象的值将覆盖Filebeat通常添加的字段(类型、源、偏移等)以防冲突。
- `add_error_key`: 如果启用了此设置，Filebeat将添加一个`error.message`和`error.type: json`key用于json解组错误，或者当配置中定义了message_key但不能使用时。
- `message_key`:  一个可选的配置设置，指定要对其应用行过滤和多行设置的JSON键。如果指定了该键，则该键必须位于JSON对象的顶层，并且与该键关联的值必须是字符串，否则不会发生过滤或多行聚合。
- `document_id`: 选项配置设置，指定用于设置文档id的JSON键。如果配置了，该字段将从原始json文档中删除，并存储在@metadata._id中


- exclude_files: 正则表达式列表，用于匹配您希望Filebeat忽略的文件。默认情况下，不排除任何文件。
下面的示例将Filebeat配置为忽略所有扩展名为gz的文件:
```
- type: container
  ...
  exclude_files: ['\.gz$']
```
- ignore_older: 如果启用此选项，Filebeat将忽略在指定时间跨度之前修改的任何文件。如果要长时间保存日志文件，配置ignore_older尤其有用。例如，如果希望启动Filebeat，但只想发送最新的文件和上周的文件，则可以配置此选项。
你可以使用2h(2小时)和5m(5分钟)这样的时间字符串。默认值为0，即禁用该设置。注释掉配置与将其设置为0具有相同的效果。
必须将ignore_older设置为大于`close_inactive`。
- scan_frequency: Filebeat多长时间检查一次指定用于收集的路径中的新文件。例如，如果指定了/var/log/*这样的glob，则使用scan_frequency指定的频率扫描目录中的文件。指定1s表示尽可能频繁地扫描目录，而不会导致Filebeat扫描过于频繁。我们不建议将该值设置为<1s。
如果您要求日志行几乎实时发送，不要使用非常低的scan_frequency，而是调整close_inactive，以便文件处理程序保持打开并不断轮询您的文件。

- enabled: 使用enabled选项启用和禁用输入。缺省情况下，enabled为true。
- tags: Filebeat包含在每个已发布事件的tags字段中的标记列表。标记使得在Kibana中选择特定事件或在Logstash中应用条件过滤变得很容易。这些标记将被添加到常规配置中指定的标记列表中。
- fields: 可选字段，您可以指定这些字段向输出添加其他信息。例如，您可以添加用于过滤日志数据的字段。字段可以是标量值、数组、字典或它们的任何嵌套组合。默认情况下，您在这里指定的字段将分组在输出文档中的fields子字典下。要将自定义字段存储为顶级字段，请将fields_under_root选项设置为true。如果在通用配置中声明了一个重复字段，那么它的值将被这里声明的值覆盖。
```
filebeat.inputs:
- type: container
  . . .
  fields:
    app_id: query_engine_12
```
- fields_under_root: 如果此选项设置为true，则自定义字段将存储为输出文档中的顶级字段，而不是分组在字段子字典下。如果自定义字段名与Filebeat添加的其他字段名冲突，则自定义字段将覆盖其他字段。
- processors: 要应用于输入数据的处理器列表。

#### 多行消息
Filebeat收集的文件可能包含跨越多行文本的消息。例如，多行消息在包含Java堆栈跟踪的文件中很常见。为了正确地处理这些多行事件，您需要在`filebeat.yml`文件中配置多行设置指定哪些行是单个事件的一部分。

下面的示例演示如何配置Filebeat中的文件流输入，以处理多行消息，其中消息的第一行以方括号([)开始。

下面的示例只适用于文件流输入，而不适用于日志输入。
```
parsers:
- multiline:
    type: pattern
    pattern: '^\['
    negate: true
    match: after
```
Filebeat获取所有不以[开头的行，并将它们与前面以[开头的行合并。例如，您可以使用此配置将多行消息中的以下行连接到单个事件:
```
[beat-logstash-some-name-832-2015.11.28] IndexNotFoundException[no such index]
    at org.elasticsearch.cluster.metadata.IndexNameExpressionResolver$WildcardExpressionResolver.resolve(IndexNameExpressionResolver.java:566)
    at org.elasticsearch.cluster.metadata.IndexNameExpressionResolver.concreteIndices(IndexNameExpressionResolver.java:133)
    at org.elasticsearch.cluster.metadata.IndexNameExpressionResolver.concreteIndices(IndexNameExpressionResolver.java:77)
    at org.elasticsearch.action.admin.indices.delete.TransportDeleteIndexAction.checkBlock(TransportDeleteIndexAction.java:75)

```
- multiline.type: 定义要使用的聚合方法。默认为`pattern`。其他选项是`count`，它允许你聚合常量行数，以及`while_pattern`，它通过不匹配选项的模式聚合行数。
- multiline.pattern: 指定要匹配的正则表达式模式。
- multiline.negate 定义模式是否为反。默认为false
- multiline.match 指定Filebeat如何将匹配的行组合为事件。设置是在`after`或`before`。这些设置的行为取决于你为negate指定的内容:
- multiline.max_lines 可以组合成一个事件的最大行数 默认500
- multiline.timeout 在指定的超时之后，即使没有发现新模式来启动新事件，Filebeat也会发送多行事件。缺省为5s。
- multiline.count_lines 聚合为单个事件的行数。
- multiline.skip_newline 设置后，多行事件将不使用行分隔符进行连接。

**Java堆栈跟踪匹配**
Java堆栈跟踪由多行组成，每一行在初始行之后，以空格开始，如下例所示:
```
Exception in thread "main" java.lang.NullPointerException
        at com.example.myproject.Book.getTitle(Book.java:16)
        at com.example.myproject.Author.getBookTitles(Author.java:25)
        at com.example.myproject.Bootstrap.main(Bootstrap.java:14)
```
要将这些行合并为Filebeat中的单个事件，请使用以下文件流的多行配置:
```
parsers:
- multiline:
    type: pattern
    pattern: '^[[:space:]]'
    negate: false
    match: after
```
此配置将合并以空格开始的任何行直到上一行。

下面是一个Java堆栈跟踪，它给出了一个稍微复杂一点的例子:
```
Exception in thread "main" java.lang.IllegalStateException: A book has a null property
       at com.example.myproject.Author.getBookIds(Author.java:38)
       at com.example.myproject.Bootstrap.main(Bootstrap.java:14)
Caused by: java.lang.NullPointerException
       at com.example.myproject.Book.getId(Book.java:22)
       at com.example.myproject.Author.getBookIds(Author.java:35)
       ... 1 more
```
要将这些行合并为Filebeat中的单个事件，请使用以下文件流的多行配置:
```
parsers:
- multiline:
    type: pattern
    pattern: '^[[:space:]]+(at|\.{3})[[:space:]]+\b|^Caused by:'
    negate: false
    match: after
```
在本例中，模式匹配以下行:
- 以空格开头的行，后面跟着单词at或…
- 以`Caused by:`开头的行


一些编程语言在行尾使用反斜杠(`\`)字符来表示行继续，如下例所示:
```
printf ("%10.10ld  \t %10.10ld \t %s\
  %f", w, x, y, z );
```
要将这些行合并为Filebeat中的单个事件，请使用以下文件流的多行配置:
```
parsers:
- multiline:
    type: pattern
    pattern: '\\$'
    negate: false
    match: before
```
该配置将以\字符结尾的任何行与其后面的行合并。

**时间戳**
来自Elasticsearch等服务的活动日志通常以时间戳开始，然后是特定活动的信息，如下例所示:
```
[2015-08-24 11:49:14,389][INFO ][env                      ] [Letha] using [1] data paths, mounts [[/
(/dev/disk1)]], net usable_space [34.5gb], net total_space [118.9gb], types [hfs]
```
```
parsers:
- multiline:
    type: pattern
    pattern: '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}'
    negate: true
    match: after
```
此配置使用negate: true和match: after设置指定任何不匹配指定模式的行属于前一行。

**应用事件**
有时你的应用程序日志包含事件，以自定义标记开始和结束，例如下面的例子:
```
[2015-08-24 11:49:14,389] Start new event
[2015-08-24 11:49:14,395] Content of processing something
[2015-08-24 11:49:14,399] End event
```
```
parsers:
- multiline:
    type: pattern
    pattern: 'Start new event'
    negate: true
    match: after
    flush_pattern: 'End event'
```
flush_pattern选项指定当前多行将被刷新的正则表达式。如果您认为模式选项指定事件的开始，那么flush_pattern选项将指定事件的结束行或最后一行。

#### 模块配置
对于模块配置，您可以在filebeat.yml文件的`filebeat.config.modules`部分中指定`path`选项。默认情况下，Filebeat加载模块中启用的`modules.d`目录模块配置。例如:
```
filebeat.config.modules:
  enabled: true
  path: ${path.config}/modules.d/*.yml
```
`path`设置必须指向` modules.d`目录。如果要使用modules命令启用和禁用模块配置

```
- module: apache
  access:
    enabled: true
    var.paths: [/var/log/apache2/access.log*]
  error:
    enabled: true
    var.paths: [/var/log/apache2/error.log*]
```