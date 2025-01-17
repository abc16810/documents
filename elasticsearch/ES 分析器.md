在 ES 中，不管是索引任务还是搜索工作，都需要使用 analyzer（分析器）。分析器，分为**内置分析器**和**自定义的分析器**（注：只有text字段支持分析器映射参数）

分析器进一步由**字符过滤器**（**Character Filters**）、**分词器**（**Tokenizer**）和**词元过滤器**（**Token Filters**）三部分组成。它的执行顺序如下

**character filters** -> **tokenizer** -> **token filters**



#### 字符过滤器（Character Filters）

字符过滤器用于在将字符流传递给标记器之前对其进行预处理

character filter 的输入是原始的文本 text，如果配置了多个，它会按照配置的顺序执行，目前 ES 自带的 character filter 主要由如下 3 类

- `html strip character filter`: 从文本中剥离 HTML 元素，并用其解码值替换 HTML 实体（如，将 **＆amp;** 替换为 **＆**）

  ```
  GET /_analyze
  {
    "tokenizer": "keyword",
    "char_filter": [
      "html_strip"
    ],
    "text": "<p>I&apos;m so <b>happy</b>!</p>"
  }
  #  I'm so happy!
  ```

  - `escaped_tags`   配置需要跳过的html标签， 例如my_custom_html_strip_char_filter 过滤器跳过删除 `<b> HTML` 元素

    ```
    {
      "settings": {
        "analysis": {
          "analyzer": {
            "my_analyzer": {
              "tokenizer": "keyword",
              "char_filter": [
                "my_custom_html_strip_char_filter"
              ]
            }
          },
          "char_filter": {
            "my_custom_html_strip_char_filter": {
              "type": "html_strip",
              "escaped_tags": [
                "b"
              ]
            }
          }
        }
      }
    }
    ```

- `mapping character filter`  自定义一个 map 映射，可以进行一些自定义的替换，如常用的大写变小写也可以在该环节设置。匹配是贪心的；  在给定点匹配最长的模式获胜。  允许替换为空字符串

  `mapping char_filter` 不像` html_strip `那样拆箱即可用，必须先进行配置才能使用，它有两个属性可以配置

  | 参数名称          | 参数说明                                                     |
  | ----------------- | ------------------------------------------------------------ |
  | **mappings**      | 一组映射，每个元素的格式为 *key => value*。                  |
  | **mappings_path** | 一个相对或者绝对的文件路径，指向一个每行包含一个 *key =>value* 映射的 UTF-8 编码文本映射文件。 |

  ```
  GET /_analyze
  {
    "tokenizer": "keyword",
    "char_filter": [
      {
        "type": "mapping",
        "mappings": [
          "٠ => 0",
          "١ => 1",
          "٢ => 2",
          "٣ => 3",
          "٤ => 4",
          "٥ => 5",
          "٦ => 6",
          "٧ => 7",
          "٨ => 8",
          "٩ => 9"
        ]
      }
    ],
    "text": "My license plate is ٢٥٠١٥"
  }
  # My license plate is 25015
  ```

  

- `Pattern Replace Character Filter` 使用 java 正则表达式来匹配应替换为指定替换字符串的字符，此外，替换字符串可以引用正则表达式中的捕获组

  Pattern Replace character filter 支持如下三个参数

  | 参数名称        | 参数说明                                                     |
  | --------------- | ------------------------------------------------------------ |
  | **pattern**     | 必填参数，一个 java 的正则表达式。                           |
  | **replacement** | 替换字符串，可以使用 **$1 ... $9** 语法来引用捕获组。        |
  | **flags**       | Java 正则表达式的标志，具体参考 java 的 java.util.regex.Pattern 类的标志属性 |

  如将输入的 text 中大于一个的空格都转变为一个空格，在 settings 时，配置示例如下

  ```
  "char_filter": {
    "multi_space_2_one": {
      "pattern": "[ ]+",
      "type": "pattern_replace",
      "replacement": " "
    },
    ...
  }
  ```

  

#### 分词器（Tokenizer）

tokenizer 即分词器，也是 analyzer 最重要的组件，它对文本进行分词；**一个 analyzer 必需且只可包含一个 tokenizer**

ES 自带默认的分词器是 standard tokenizer，标准分词器提供基于语法的分词（基于 Unicode 文本分割算法），并且适用于大多数语言

此外有很多第三方的分词插件，如中文分词界最经典的 ik 分词器，它对应的 tokenizer 分为 ik_smart 和 ik_max_word，一个是智能分词（针对搜索侧），一个是全切分词（针对索引侧）

ES 默认提供的分词器 standard 对中文分词不优化，效果差，一般会安装第三方中文分词插件，通常首先 [elasticsearch-analysis-ik](https://github.com/medcl/elasticsearch-analysis-ik) 插件，它其实是 ik 针对的 ES 的定制版

分词器接收一个字符流，将其分解为单个令牌（通常是单个单词），并输出一个令牌流。  例如，只要看到任何空格，空格标记器就会将文本分解为标记。  它将转换文本`"Quick brown fox!"`成术语`[Quick, brown, fox!]`

分词器还负责记录以下内容

- 每个术语的顺序或位置（用于短语和单词邻近查询）
- 术语所代表的原始单词的开始和结束字符偏移量（用于突出显示搜索片段）。
- *Token* 类型，生成的每个术语的分类，例如 <ALPHANUM>、<HANGUL> 或 <NUM>。  更简单的分析器只产生`word` *Token* 类型

**面向词的分词器**

- `Standard Tokenizer`  标准分词器提供基于语法的分词（基于 Unicode 文本分割算法），并且适用于大多数语言 默认

- `Letter Tokenizer` 每当遇到不是字母的字符时，letter 分词器就会将文本分成术语

  ```
  POST _analyze
  {
    "tokenizer": "letter",
    "text": "The 2 QUICK Brown-Foxes jumped over the lazy dog's bone."
  }
  # [ The, QUICK, Brown, Foxes, jumped, over, the, lazy, dog, s, bone ]
  ```

- `lowercase tokenizer`  lowercase分词器和letter分词器一样，只要遇到不是字母的字符，就会将文本分成术语，但它也会将所有术语小写。

- `Whitespace Tokenizer`   每当遇到任何空白字符时，whitespace分词器都会将文本划分为术语

- `UAX URL Email Tokenizer` uax_url_email 分词器类似于标准分词器，只是它将 URL 和电子邮件地址识别为单个令牌

  ```
  {
    "tokenizer": "uax_url_email",
    "text": "Email me at john.smith@global-international.com"
  }
  # [ Email, me, at, john.smith@global-international.com ]
  ```

- `Classic Tokenizer`  经典的分词器是基于语法的英语分词器

- `Thai Tokenizer` 泰语分词器将泰语文本分割成单词

**局部分词器**

这些分词器将文本或单词分解成小片段，以进行部分单词匹配

- `N-Gram Tokenizer`  当遇到任何指定字符列表（例如空格或标点符号）时，ngram 分词器可以将文本分解为单词，然后它返回每个单词的 n-gram：连续字母的滑动窗口，例如 quick → [qu, ui , ic, ck]

  N-gram 就像一个在单词上移动的滑动窗口——一个指定长度的连续字符序列。  它们对于查询不使用空格或复合词长的语言（如德语）很有用

  ```
  POST _analyze
  {
    "tokenizer": "ngram",
    "text": "Quick Fox"
  }
  # [ Q, Qu, u, ui, i, ic, c, ck, k, "k ", " ", " F", F, Fo, o, ox, x ]
  ```

  - `min_gram`  以 gram 为单位的最小字符长度。  默认为 1
  - `max_gram`  以 gram 为单位的最大字符长度。  默认为 2

- `Edge N-Gram Tokenizer` edge_ngram 分词器可以在遇到任何指定字符列表（例如空格或标点符号）时将文本分解为单词，然后返回每个单词的 n-gram，这些单词锚定到单词的开头，例如 `quick` →
  `[q, qu, qui, quic, quick]`  Edge N-Grams 对于搜索即键入查询很有用

  ```
  POST _analyze
  {
    "tokenizer": "edge_ngram",
    "text": "Quick Fox"
  }
  # [ Q, Qu ]
  ```

  通常我们建议在索引时和搜索时使用相同的分析器。  在 edge_ngram 分词器的情况下，建议是不同的。  只有在索引时使用 edge_ngram 标记器才有意义，以确保部分单词可用于索引中的匹配。  在搜索时，只需搜索用户输入的术语，例如：Quick Fo

  https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-edgengram-tokenizer.html

**结构化文本分词器**

- `Keyword Tokenizer ` 关键字分词器是一个“noop”标记器，它接受给定的任何文本并将完全相同的文本输出为单个术语，它可以和`lowercase` 词元过滤器结合提供标准化分析的术语

  ```
  {
    "tokenizer": "keyword",
    "filter": [
      "lowercase"
    ],
    "text": "john.SMITH@example.COM"
  }
  # john.smith@example.com
  ```

- `Pattern Tokenizer ` 模式分词器使用正则表达式在匹配单词分隔符时将文本拆分为术语，或者将匹配的文本捕获为术语（java正则表达式） 默认模式是 `\W+`，它会在遇到非单词字符时拆分文本

  ```
  POST _analyze
  {
    "tokenizer": "pattern",
    "text": "The foo_bar_size's default is 5."
  }
  # [ The, foo_bar_size, s, default, is, 5 ]
  
  ```

- `Simple Pattern Tokenizer` simple_pattern 分词器使用正则表达式将匹配的文本捕获为术语。  它使用正则表达式功能的受限子集（它支持的正则表达式功能集比模式更有限），并且通常比模式分词器更快

  例如将 simple_pattern 分词器配置为生成三位数字的术语

  ```
  {
    "settings": {
      "analysis": {
        "analyzer": {
          "my_analyzer": {
            "tokenizer": "my_tokenizer"
          }
        },
        "tokenizer": {
          "my_tokenizer": {
            "type": "simple_pattern",
            "pattern": "[0123456789]{3}"
          }
        }
      }
    }
  }
  
  POST xx/_analyze
  {
    "analyzer": "my_analyzer",
    "text": "fd-786-335-514-x"
  }
  # [ 786, 335, 514 ]
  ```

- `Char Group Tokenizer`  char_group 分词器可通过要拆分的字符集进行配置，这通常比运行正则表达式简单

  ```
  POST _analyze
  {
    "tokenizer": {
      "type": "char_group",
      "tokenize_on_chars": [
        "whitespace",
        "-",
        "\n"
      ]
    },
    "text": "The QUICK brown-fox"
  }
  ```

  - `tokenize_on_chars`  一个列表，其中包含用于标记字符串的字符列表。  每当遇到此列表中的字符时，就会启动一个新标记。  这接受单个字符
  - `max_token_length` 最大令牌长度。  如果看到超过此长度的令牌，则以 max_token_length 间隔对其进行拆分 默认255

- `Simple Pattern Split Tokenizer` simple_pattern_split 分词器使用与 simple_pattern 分词器相同的受限正则表达式子集，但在匹配时拆分输入，而不是将匹配作为项返回

  - `pattern` Lucene 正则表达式，默认为空字符串

  ```
  {
    "settings": {
      "analysis": {
        "analyzer": {
          "my_analyzer": {
            "tokenizer": "my_tokenizer"
          }
        },
        "tokenizer": {
          "my_tokenizer": {
            "type": "simple_pattern_split",
            "pattern": "_"
          }
        }
      }
    }
  }
  ```

- `Path Tokenizer`  path_hierarchy 分词器采用像文件系统路径一样的层次值，在路径分隔符上拆分，并为树中的每个组件发出一个术语，例如 /foo/bar/baz → [/foo, /foo/bar, /foo/bar /baz]



#### 词元过滤器（Token Filters）

token filters 叫词元过滤器，或词项过滤器，对 tokenizer 分出的词进行过滤处理。常用的有转小写、停用词处理、同义词处理等等。**一个 analyzer 可包含 0 个或多个词项过滤器，按配置顺序进行过滤**

常用词元过滤器

- **stop**   停用词处理未自定义时，过滤器默认去除以下英文停用词`a`, `an`, `and`, `are`, `as`, `at`, `be`, `but`, `by`, `for`, `if`, `in`, `into`, `is`, `it`, `no`, `not`, `of`, `on`, `or`, `such`, `that`, `the`, `their`, `then`, `there`, `these`, `they`, `this`, `to`, `was`, `will`, `with` 除了英语之外，停止过滤器还支持多种语言的预定义停止词列表。  您还可以将自己的停用词指定为数组或文件

  配置参数

  - `stopwords` （可选，字符串或字符串数组）语言值，例如 `_arabic_ `或 `_thai_`。  默认为`_english_` 每个语言值对应于 Lucene 中预定义的停用词列表。  有关受支持的语言值及其停用词，请参阅按语言列出的停用词  如停止过滤器，仅删除停用词 and、is 和 the `"stopwords": [ "and", "is", "the" ]`
  - `ignore_case` （可选，布尔值）如果为真，则停止词匹配不区分大小写。  例如，如果为真，则匹配并删除 The、THE 或 the 的停用词。  默认False

  ```
        "filter": {
          "my_custom_stop_words_filter": {
            "type": "stop",
            "ignore_case": true
          }
        }
  ```

- **synonym** 同义词标记过滤器允许在分析过程中轻松处理同义词。  同义词是使用配置文件配置的

  - `expand`   默认true 该参数决定映射行为的模式，默认为 true，表示扩展模式，具体示例如下

    当 **expand == true** 时

    `ipod, i-pod, i pod`  等价于 `ipod, i-pod, i pod => ipod, i-pod, i pod`

    当 **expand == false** 时

    `ipod, i-pod, i pod`  仅映射第一个单词，等价于 `ipod, i-pod, i pod => ipod`

  - `lenient`  默认false  如果 true 在解析同义词配置时忽略异常。  需要注意的是，只有那些无法解析的同义词规则才会被忽略

  elasticsearch 的同义词有如下两种形式  

  1. 单向同义词 `ipod, i-pod, i pod => ipod ` 单向同义词不管索引还是检索时，箭头左侧的词都会映射成箭头右侧的词；
  2. 双向同义词  `马铃薯, 土豆, potato`  ， `universe, cosmos ` 双向同义词是索引时，都建立同义词的倒排索引，检索时，同义词之间都会进行倒排索引的匹配

  同义词的文档化时，需要注意的是，同一个词在不同的同义词关系中出现时，其它同义词之间不具有传递性，这点需要注意。所以多个同义词要写在一起

- **Trim**  从流中的每个标记中删除前导和尾随空格。  虽然这可以更改令牌的长度，但修剪过滤器不会更改令牌的偏移量。

  许多常用的标记器，例如`standard`或`Whitespace`分词器，默认删除空格。  使用这些标记器时，您不需要添加单独的修剪过滤器

  ```
  GET _analyze
  {
    "tokenizer" : "keyword",
    "filter" : ["trim"],
    "text" : " fox "
  }
  # fox
  ```

- **unique**  从流中删除重复的标记。 

  ```
  {
    "tokenizer": "whitespace",
    "filter": [
      "stop",
      "unique"
    ],
    "text": "the quick fox jumps the lazy fox aa aa"
  }
  # quick fox jumps lazy aa
  ```

- **uppercase ** 将标记文本更改为大写

- **Truncate** 截断超过指定字符限制的标记。  此限制默认为 10，但可以使用长度参数进行自定义

  ```
  GET _analyze
  {
    "tokenizer" : "whitespace",
    "filter" : ["truncate"],
    "text" : "the quinquennial extravaganza carried on"
  }
  # [ the, quinquenni, extravagan, carried, on ]
  ```

  - `length`  默认10

- **Snowball**  使用除梗器,对单词进行除梗的过滤器。语言参数可以控制除梗器，有如下的语言可供选择

- **reverse **  反转流中的每个标记。  例如，您可以使用`reverse` 过滤器将 cat 更改为 tac

- **remove_duplicates** 删除相同位置的重复标记

  ```
  GET _analyze
  {
    "tokenizer": "whitespace",
    "filter": [
      "keyword_repeat",
      "stemmer",
      "remove_duplicates"
    ],
    "text": "jumping dog"
  }
  ```

- **pattern_replace**  使用正则表达式匹配和替换标记子字符串。pattern_replace 过滤器使用 Java 的正则表达式语法。  默认情况下，过滤器将匹配的子字符串替换为空子字符串 ("")。  替换子字符串可以使用 Java 的 $g 语法从原始标记文本中引用捕获组 写得不好的正则表达式可能运行缓慢或返回 StackOverflowError，导致运行该表达式的节点突然退出

- **ngram** 从一个令牌形成指定长度的 n-gram

- **lowercase**   将标记文本更改为小写

- **length ** 删除比指定字符长度更短或更长的标记。  例如，您可以使用长度过滤器来排除短于 2 个字符的标记和长于 5 个字符的标记

  - `min`  默认0
  - `max` 默认`2^31-1` or `2147483647`

  ```
       "filter": {
          "length_2_to_10_char": {
            "type": "length",
            "min": 2,
            "max": 10
          }
        }
  ```

- **keep_words**  仅保留包含在指定单词列表中的标记



#### 内置分析器

Elasticsearch 附带了广泛的内置分析器，无需进一步配置即可用于任何索引

- [Standard Analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-standard-analyzer.html) 标准分析器将文本划分为单词边界上的术语，如 Unicode 文本分割算法所定义。  它删除了大多数标点符号、小写术语，并支持删除停用词

  ```
  {
    "analyzer": "standard",
    "text": "The 2 QUICK Brown-Foxes jumped over the lazy dog's bone."
  }
  # 输出
  [ the, 2, quick, brown, foxes, jumped, over, the, lazy, dog's, bone ]
  ```

  - `max_token_length`  最大令牌长度。  如果看到超过此长度的令牌，则以 max_token_length 间隔对其进行拆分。  默认为 255

  - `stopwords`  预定义的停用词列表，如`_english_ `或包含停用词列表的数组。  默认为`_none_`

    ```
    "my_english_analyzer": {
              "type": "standard",
              "max_token_length": 5,    # 表明最大单词的长度为5
              "stopwords": "_english_"
            }
    # 输出
    [ 2, quick, brown, foxes, jumpe, d, over, lazy, dog's, bone ]
    ```

  Tokenizer 为 `Standard Tokenizer`

  Token Filters 为 `Lower Case Token Filter`  [Stop Token Filter](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-stop-tokenfilter.html) (disabled by default)

- [Simple Analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-simple-analyzer.html) 只要遇到不是字母的字符，简单的分析器就会将文本划分为术语。  它小写所有术语

  ```
  POST _analyze
  {
    "analyzer": "simple",
    "text": "The 2 QUICK Brown-Foxes jumped over the lazy dog's bone."
  }
  # [ the, quick, brown, foxes, jumped, over, the, lazy, dog, s, bone ]
  ```

  Tokenizer 为 `Lowercase tokenizer`

- [Whitespace Analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-whitespace-analyzer.html)  每当遇到任何空白字符时，`whitespace` 分析器都会将文本分成术语。  它不会小写术语

  Tokenizer 为 `whitespace Tokenizer`

-   [Stop Analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-stop-analyzer.html)   `stop` 分析器就像`simple` 分析器，但也支持去除停止词

   Tokenizer 为 `Lowercase Tokenizer`

   Token Filters 为`Stop Token Filter`

  ```
  {
    "settings": {
      "analysis": {
        "filter": {
          "english_stop": {
            "type":       "stop",
            "stopwords":  "_english_" 
          }
        },
        "analyzer": {
          "rebuilt_stop": {
            "tokenizer": "lowercase",
            "filter": [
              "english_stop"          
            ]
          }
        }
      }
    }
  }
  ```

- [Keyword Analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-keyword-analyzer.html) 关键字分析器是一个“noop”分析器，它接受给定的任何文本并输出完全相同的文本作为单个术语

  Tokenizer 为`Keyword Tokenizer`

- [Pattern Analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-pattern-analyzer.html)  模式分析器使用正则表达式将文本拆分为术语。  它支持小写和停用词

   Tokenizer 为 `Pattern Tokenizer`

   Token Filters 为`Lower Case Token Filter`

- [Language Analyzers](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-lang-analyzer.html)

- [Fingerprint Analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-fingerprint-analyzer.html)  指纹分析仪是一种专业分析仪，可创建可用于重复检测的指纹

- **snowball**   一个snowball类型的analyzer是由standard tokenizer和standard filter、lowercase filter、stop filter、snowball filter这四个filter构成的 （snowball analyzer 在Lucene中通常是不推荐使用的）



#### elasticsearch-plugin 使用

在安装 elasticsearch-analysis-ik 第三方之前，我们首先要了解 es 的插件管理工具 **elasticsearch-plugin** 的使用

现在的 elasticsearch 安装完后，在安装目录的 bin 目录下会存在 elasticsearch-plugin 命令工具，用它来对 es 插件进行管理

```
bin/elasticsearch-plugin
#  安装指定的插件到当前 ES 节点中
elasticsearch-plugin install {plugin_url}

#  显示当前 ES 节点已经安装的插件列表
elasticsearch-plugin list

#  删除已安装的插件
elasticsearch-plugin remove {plugin_name}
```

在安装插件时，要保证安装的插件与 ES 版本一致

**elasticsearch-analysis-ik 安装**

```
./bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v{X.X.X}/elasticsearch-analysis-ik-{X.X.X}.zip
```

