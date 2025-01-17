[Alertmanager](https://github.com/prometheus/alertmanager)通过命令行标志和配置文件进行配置。  虽然命令行标志配置不可变的系统参数，但配置文件定义了抑制规则、通知路由和通知接收器

Prometheus创建并向Alertmanager发送警报，Alertmanager然后根据不同的接收器的标签向不同的接收器发送通知。接收端可以是多种集成中的一种，包括:Slack、PagerDuty、email，或者通过通用的webhook接口进行定制集成

```cpp
curl -lv -X POST http://localhost:9093/-/reload
```

Alertmanager 可以在运行时重新加载其配置。  如果新配置格式不正确，则不会应用更改并记录错误

```
global:
  resolve_timeout: 5m  # 默认 解决超时时间
  smtp_smarthost: 'smtp.qq.com:25'             #邮箱smtp服务器
  smtp_from: 'xx@qq.com'              #发送邮箱名称
  smtp_auth_username: 'xx@qq.com'              #邮箱名称
  smtp_auth_password: 'xx'                #邮箱密码或授权码
  smtp_require_tls: false
# 自定义通知模板
templates:  
  [ - <filepath> ... ]  # templates/*.tmpl
# 路由块定义了路由树中的一个节点及其子节点。如果没有设置，它的可选配置参数将从其父节点继承。
route:
  receiver: 'default-receiver'  # 接收器
  group_by: ['alertname', 'job'] # 告警分组
  group_wait: 10s #组报警等待时间 第一次的告警信息在间隔多长时间后发送给receiver
  group_interval: 10s #组报警间隔时间
  repeat_interval: 1m #在连续告警触发的情况下，重复发送告警的时间间隔

  routes: # 子路由树，不匹配子路由下的所有警告，将保持在根节点，并被分派到'default-receiver'
  # 该路由对警告标签执行正则表达式匹配，以捕获与服务列表相关的警报
  - match_re:
    service: ^(foo1|foo2|baz)$
    receiver: team-X-mails
  - receiver: 'database-pager'
    group_wait: 10s
    matchers:
    - service=~"mysql|cassandra"  # 所有警告service=mysql或service=cassandra
  - receiver: 'frontend-pager'
    group_by: [product, environment] # 它们按改配置分组，而不是父节点分组。
    matchers:
    - team="frontend"  # 所有带有team=frontend标签的警报都匹配这个子路径
    
# 告警抑制 
inhibit_rules:
- source_match:   # source_matchers
    severity: 'critical'
  target_match:
    severity: 'warning'
  equal: ['alertname', 'instance']

# 接收器
receivers:
- name: 'default-receiver'
  email_configs:
  - to: 'xx@qq.com'  # 告警接受
    send_resolved: true   # 是否通知告警已解决的警报
    headers: { Subject: "[WARN] 报警邮件" }   #邮件主题信息 如果不写headers也可以在模板中定义默认加载email.default.subject这个模板
    html: '{{ template "email.my.html" . }}' #应用哪个模板 必须在模板中定义 默认email.default.html
```

#### 告警模板

发送给接收者的通知是通过模板构造的。Alertmanager提供了默认模板，但也可以对其进行定制。为了避免混淆，重要的是要注意Alertmanager模板不同于Prometheus中的模板，然而，Prometheus的模板也在警告规则标签/注解中包含了这个模板

Alertmanager的通知模板是基于Go模板系统的。请注意，有些字段是作为文本计算的，而其他字段是作为HTML计算的，这会影响转义。

[官方模板](https://github.com/prometheus/alertmanager/blob/master/template/default.tmpl)

```
# 模板变量 在模板中定义了变量后，在整个模板中都能使用
{{ $Name := "fei" }}
hello {{ $Name }}
# define 定义了一个名为"this.is.template"的模板
{{ define "this.is.template" }} ... {{ end }}
# Range  模板里使用range来进行遍历数据，类似于jinja2模板语言中的for
type Info struct {
    Name string
    Age int
}
{{ range .Info }}
name: {{ .Name }}
age: {{ .Age }}
{{ end }}
```

**内置函数**

- title: 将字符串转换为首字母大写
- toUpper: 所有字母转换成大写
- toLower: 所有字母转换成小写
- join: 拼接字符串
- safeHtml: 将字符串标记为不需要自动转义的html
- len: 获取长度

    {{ "abcd" | toUpper }}
    {{ "ABCD" | toLower }}
    {{ .Values | join "," }}
**移除空格**

写过ansible-playbook的一定知道，在使用`jinja2`写模板的时候，缩进、空格会让人很头疼，go语言的模板同样也是如此，也是使用`-`减号来做处理

```
{{- }} #去掉左边的空格
{{ -}} #去掉右边的空格
{{- -}} #去掉两边所有的空格
```

**数据**

.Receiver: 接收器的名称
.Status: 如果正在告警，值为firing，恢复为resolved
.Alerts: 所有告警对象的列表，是一个列表，告警对象的数据结构可以看下面`alert`部分
.Alerts.Firing: 告警列表
.Alerts.Resolved: 恢复列表
.GroupLabels: 告警的分组标签  kv类型
.CommonLabels: 所有告警共有的标签 kv类型
.CommonAnnotations: 所有告警共有的注解 kv类型
.ExternalURL: 告警对应的alertmanager连接地址

**Alert**

- `Status`: 当前这一条报警的状态。`firing`(告警)或`resolved`(恢复)
- `Labels`: 当前这一条报警的标签
- `Annotations`: 当前这一条报警的注解
- `StartsAt`: 当前这一条报警的开始时间
- `EndsAt`: 当前这一条报警的结束时间
- `GeneratorURL`: 告警对应的alertmanager链接地址
- `Fingerprint` 警报指纹

**KV**

除了直接访问存储为KV的数据(标签和注释)外，还有排序、删除和查看LabelSets的方法

- `SortedPairs`: 排序
- `Remove `: 删除一个key
- `Names`: 返回标签集中标签名的名称列表。
- `Values`: 返回标签集中标签名的值列表。

#### 告警分组

告警分组主要围绕上面的的四个属性来。
所有从prometheus来的告警，都会进行分组，告警的发送也是按照分组来的，group_by就是按照标签分组，一般alertname会作为选择，就是告警的名称，其次后面会根据业务来区分，例如我上面写的job。他会按照job再进行一次分组。这样的好处是可以合并告警信息

#### 路由

路由块定义路由树中的节点及其子节点。如果没有设置，则从其父节点继承其可选配置参数。

每个警报在已配置路由树的顶部节点，这个节点必须匹配所有警报。然后遍历所有的子节点。如果continue设置成false, 当匹配到第一个子节点时，它会停止下来；如果continue设置成true, 则警报将继续匹配后续的兄弟姐妹节点。如果一个警报不匹配一个节点的任何子节点，这个警报将会基于当前节点的配置参数来处理警报。

#### 告警抑制

当存在匹配另一组匹配器的警报(`source`)时，抑制规则对匹配一组匹配器的警报(`target`)进行静音。对于相等列表中的标签名，目标和源警报都必须具有相同的标签值

正如上面的告警规则，critical是高级别，warning是低级别。当一个值是critical的时候，满足高级别，进行高级别的告警，也同时满足低级别，所以也会产生一个低级别的告警，这完全是两条不一样的告警信息，但表达的内容是相同的。而且还有包含关系，都是高级别的了，肯定也满足低级别的条件。此时有低级别的告警就不合适了。
符合人们理解的情况是，只报最高级别的告警。这里就需要抑制功能了

抑制的功能其实就是根据label进行去重的操作。从语义上讲，缺少的标签和值为空的标签是一回事。因此，如果在equal中列出的所有标签名称在源警报和目标警报中都缺失，则应用抑制规则

#### 告警Sliences 静默

静默是一个非常简单的方法，可以在给定时间内简单地忽略所有警报。slience基于matchers配置，类似路由树。来到的警告将会被检查，判断它们是否和活跃的slience相等或者正则表达式匹配。如果匹配成功，则不会将这些警报发送给接收者。

Silences在Alertmanager的web接口中配置

#### 高可用

Alertmanager支持通过配置创建集群，实现高可用性。这可以使用——cluster-*标志来配置。`--cluster.listen-address`可以指定监听的端口。`--cluster.peer`则是选择要监听的alertmanager。他是通过gossip进行传播。默认情况下是启用的

不要在Prometheus和它的Alertmanagers之间负载平衡流量，而是让Prometheus找到所有Alertmanagers的列表

> 在alertmanager 0.15和更高版本中，UDP和TCP都需要集群工作。--cluster.listen-address  集群监听地址（默认"0.0.0.0:9094",  空字符串禁用HA模式）

要将Prometheus 1.4或更高版本的实例指向多个Alertmanagers，请在`Prometheus.yml`中配置它们

```
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager1:9093
      - alertmanager2:9093
      - alertmanager3:9093
```

