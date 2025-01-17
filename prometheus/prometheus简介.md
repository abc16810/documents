#### Prometheus

Prometheus是一个开源的系统监控和警报工具包，最初构建于SoundCloud。自2012年启动以来，许多公司和组织都采用了Prometheus，该项目拥有非常活跃的开发人员和用户社区。它现在是一个独立的开源项目，独立于任何公司进行维护。为了强调这一点，并澄清项目的治理结构，Prometheus于2016年加入原生云基金会(Cloud Native Computing Foundation)，成为继Kubernetes之后第二个托管项目



Prometheus收集并存储它的度量作为时间序列数据，即度量信息与记录它的时间戳一起存储，还有可选的称为标签的键值对

#### Prometheus特性

- 时间序列数据的多维数据模型，由度量名称和键/值对标识
- 灵活的查询语言（PromQL）
- 不依赖分布式存储;单个服务器节点是自主的
- 通过基于HTTP的pull方式采集时序数据
- 通过中间网关支持时间序列的推送
- 通过服务发现或者静态配置来发现目标服务对象
- 支持多种多样的图表和界面展示，比如Grafana等。
- 高效的存储，每个采样数据占3.5 bytes左右，300万的时间序列，30s间隔，保留60天，消耗磁盘大概200G
- 做高可用，可以对数据做异地备份，联邦集群，部署多套prometheus，pushgateway上报数据



#### 组件

罗米修斯生态系统由多个组件组成，其中许多组件是可选的:

- `Prometheus Server`: 用于收集和存储时间序列数据。

- `Client Library`: 客户端库，检测应用程序代码，当Prometheus抓取实例的HTTP端点时，客户端库会将所有跟踪的metrics指标的当前状态发送到prometheus server端。

- `Exporters`: prometheus支持多种exporter，通过exporter可以采集metrics数据，然后发送到prometheus server端，所有向promtheus server提供监控数据的程序都可以被称为exporter

- `Alertmanager`: 从 Prometheus server 端接收到 alerts 后，会进行去重，分组，并路由到相应的接收方，发出报警，常见的接收方式有：电子邮件，微信，钉钉, slack等。

- `Grafana`：监控仪表盘，可视化监控数据

- `pushgateway`: 各个目标主机可上报数据到pushgateway，然后prometheus server统一从pushgateway拉取数据。

####  架构

普罗米修斯的架构和它的一些生态系统组件

![Prometheus architecture](https://prometheus.io/assets/architecture.png)

Prometheus server由三个部分组成，Retrieval，Storage，PromQL

- `Retrieval`负责在活跃的target主机上抓取监控指标数据
- `Storage`存储主要是把采集到的数据存储到磁盘中
- `PromQL`是Prometheus提供的查询语言模块。



#### 原理

- Prometheus  Server负责定时去目标上抓取metrics(指标)数据，每个抓取目标需要暴露一个http服务的接口给它定时抓取。Prometheus支持通过配置文件、文本文件、Zookeeper、Consul、DNS  SRV  Lookup等方式指定抓取目标。Prometheus采用PULL的方式进行监控，即服务器可以直接通过目标PULL数据或者间接地通过中间网关来Push数据。

- Prometheus在本地存储抓取的所有数据，并通过一定规则进行清理和整理数据，并把得到的结果存储到新的时间序列中。通过配置报警规则，把触发的报警发送到alertmanager

- Prometheus通过PromQL和其他API可视化地展示收集的数据。Prometheus支持很多方式的图表可视化，例如Grafana、自带的Promdash以及自身提供的模版引擎等等。Prometheus还提供HTTP  API的查询方式，自定义所需要的输出。

- PushGateway支持Client主动推送metrics到PushGateway，而Prometheus只是定时去Gateway上抓取数据。

- Alertmanager是独立于Prometheus的一个组件，可以支持Prometheus的查询语句，提供十分灵活的报警方式，如发送报警到邮件，微信或者钉钉等