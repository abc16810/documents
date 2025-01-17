#### fleet server

Fleet Server是Elastic Stack的一个组件，用于统一管理Elastic Agents。它作为作为服务器的主机上的Elastic Agent的一部分启动。一个Fleet Server进程可以支持多个Elastic Agent连接，并作为一个控制平面，用于更新代理策略、收集状态信息和协调跨Elastic Agent的操作

Fleet Server是Elastic Agents与Elasticsearch通信的机制

- 当创建一个新的代理策略时，它被保存到Elasticsearch中
- 要在策略中注册，Elastic Agents使用为身份验证生成的注册密钥向Fleet Server发送一个请求。
- fleet Server接收请求并从Elasticsearch获取代理策略，然后将策略发送给该策略中注册的所有Elastic Agents 
- Elastic Agent通过策略中的配置信息收集数据并发送给Elasticsearch
- Elastic Agent检查到Fleet Server进行更新，保持一个开放的连接
- 当策略更新时，Fleet Server从Elasticsearch检索更新的策略，并将其发送到连接的Elastic Agents

![Fleet Server handles communication between Elastic Agent](https://www.elastic.co/guide/en/fleet/7.17/images/fleet-server-communication.png)

Fleet Server使用一个服务令牌与Elasticsearch通信，Elasticsearch包含一个Fleet - Server服务帐户。每个Fleet Server都可以使用自己的服务令牌，并且可以跨多个服务器共享它(不推荐)。为每个服务器使用单独的令牌的好处是，您可以单独使每个令牌失效

默认情况下，Fleet Server开放端口为**8220**

#### 常规模式

要部署自我管理的Fleet Server，请安装Elastic Agent并将其注册到包含Fleet Server集成的代理策略中

您只能在每个主机上安装单个Elastic Agent，这意味着您不能在同一主机上同时运行Fleet Server和另一个Elastic Agent，除非您部署了容器化的Fleet Server。

- 登录Kibana，进入“Management > Fleet”。第一次访问此页面时，可能需要一分钟来加载

- 单击Fleet settings，并在Fleet Server hosts字段中指定Elastic Agents将用于连接到Fleet Server的url。例如，`http://192.0.2.1:8220`，其中192.0.2.1是要安装Fleet Server的主机IP 

  ```
  上述为快速部署模式： Fleet 服务器将生成自签名证书。必须使用 --insecure 标志注册后续代理。不推荐用于生产用例。
  配置安全传输 指定https://ip[域名]:8220  # 生成环境，提供您自己的证书。注册到 Fleet 时，此选项将需要代理指定证书密钥
  如果选择生产部署模式，请了解如何使用生成证书在自我管理的Fleet Server在集群中加密传输。
  ```

- 在Elasticsearch hosts字段中，指定弹性代理将发送数据的Elasticsearch url。例如`https://192.0.2.0:9200`

  ```
  如果 es 配置的https  指定为https://ip[域名]:9200
  ```

- 保存并应用设置，生成服务令牌

- 单击Agents选项卡，并按照产品中的说明添加一个Fleet服务器

install命令将Elastic Agent安装为托管服务，并将其注册到Fleet Server策略中。例如，下面的命令安装了一个Fleet Server，并使用自签名证书:

```
sudo ./elastic-agent install  -f \
  --fleet-server-es=http://es:9200 \
  --fleet-server-service-token=AAEbAWVsYXN0aWMvZmxlaXQtc2VydmVzL3Rva2VuLTE2MeIzNTY1NTQ3Mji6dERXeE9XbW5RRTZqNlJMWEdIRzAtZw \
  --fleet-server-policy=27467ed1-1bfd-11ec-9b88-a7c3d83e2897
  --fleet-server-insecure-http   # 不安全模式
```

#### 对Elastic Agents、Fleet Server和Elasticsearchedit之间的流量进行加密

**1. 使用自我管理的Fleet Server对集群中的流量进行加密**

Elastic Agents需要使用pem格式的CA证书向Elasticsearch发送加密数据。如果您遵循了为Elastic Stack配置安全性中的步骤，您的证书将位于p12文件中。要转换它，使用openssl:

```
openssl pkcs12 -in path.p12 -out cert.crt -clcerts -nokeys
openssl pkcs12 -in path.p12 -out private.key -nocerts -nodes
```

注： 目前不支持密钥密码

1. 生成CA (certificate authority)。如果使用已有的CA，请跳过此步骤

   ```
   elasticsearch-certutil ca --pem
   # 此命令创建一个zip文件，其中包含用于签名Fleet Server证书的CA证书和密钥。解压zip文件:
   # unzip elastic-stack-ca.zip
   # ls ca/
   ca.crt  ca.key
   ```

2. 使用证书颁发机构为Fleet Server生成证书

   ```
   elasticsearch-certutil cert \
     --name fleet-server \
     --ca-cert /path/to/ca/ca.crt \
     --ca-key /path/to/ca/ca.key \
     --dns your.host.name.here \
     --ip 192.0.2.1 \
     --pem
    # 其中dns和ip指定fleet服务器的名称和ip地址。对计划部署的每个Fleet Server运行此命令
    # 这个命令创建一个包含.crt和.key文件的zip文件。解压zip文件
   ```

   将文件存储在安全的位置。稍后，您将需要这些文件来加密Elastic Agents和Fleet Server之间的通信

**2. 配置 **

Fleet Server需要CA证书才能安全地连接到Elasticsearch。它还需要公开一个Fleet Server证书，以便其他Elastic Agents可以安全地连接到它

对于本节中的步骤，假设您有以下文件

|                        |                                                              |
| ---------------------- | ------------------------------------------------------------ |
| ca.crt                 | 用于连接Fleet Server的CA证书。这是用于为Fleet Server生成证书和密钥的CA |
| `fleet-server.crt`     | 为Fleet Server生成的证书（上述第二步生成）                   |
| `fleet-server.key`     | 为Fleet Server生成的私钥（上述第二步生成）                   |
| `elasticsearch-ca.crt` | 用于连接Elasticsearch的CA证书。这是用于为Elasticsearch生成证书的CA |

配置fleet 设置

- 在Kibana进入**Management > Fleet**.
- 在右上角单击“Fleet settings”，设置适用于所有Fleet管理的Elastic Agents的连接详细信息

![Screen capture that shows Fleet Server hosts](https://www.elastic.co/guide/en/fleet/7.17/images/fleet-settings-ssl.png)

- 在Fleet Server hosts字段中，指定Elastic Agents将用于连接到Fleet Server的url。例如，`https://192.0.2.1:8220`，其中192.0.2.1是要安装Fleet Server的主机IP

- 在Elasticsearch host字段中，指定Elastic Agents将发送数据的Elasticsearch url。例如,`https://192.0.2.0:9200`

  对两个主机设置都使用https协议。也允许基于dns的名称

- 配置`ssl.certificate_authority`，并指定用于连接Elasticsearch的CA证书。您可以指定文件路径列表(如果文件可用的话)，或者直接在YAML配置中嵌入证书。如果指定了证书的路径，则证书必须在运行Elastic Agents的主机上可用

  ```
  ssl.certificate_authorities: ["/path/to/your/elasticsearch-ca.crt"] 
  ```

在该主机上安装一个Elastic Agent作为Fleet Server，并配置使用TLS协议:

如果您还没有一个Fleet Server服务令牌，请单击Fleet中的Agents选项卡，然后按照说明立即生成服务令牌

在提取Fleet Server的目录中，运行install命令并指定要使用的证书

下面的命令将Elastic Agent安装为服务，注册到Fleet Server策略中，并启动服务。

```
sudo ./elastic-agent install -f \
   --url=https://192.0.2.1:8220 \
   --fleet-server-es=https://192.0.2.0:9200 \
   --fleet-server-service-token=AAEBAWVsYXm0aWMvZmxlZXQtc2XydmVyL3Rva2VuLTE2MjM4OTAztDU1OTQ6dllfVW1mYnFTVjJwTC2ZQ0EtVnVZQQ \
   --fleet-server-es-ca=/path/to/elasticsearch-ca.crt \ # 用于连接Elasticsearch的CA证书
   --certificate-authorities=/path/to/ca.crt \  # 用于连接Fleet Server的CA证书
   --fleet-server-cert=/path/to/fleet-server.crt \   # 要用于公开的Fleet Server HTTPS端点的证书
   --fleet-server-cert-key=/path/to/fleet-server.key 
```



安装Elastic Agents并在Fleet中注册它们

Elastic Agents连接到受保护的Fleet Server时，需要通过Fleet Server使用的CA证书。Elasticsearch使用的CA证书已经在代理策略中指定，因为它是在Kibana中的Fleet设置下设置的。您不需要在命令行上传递它

下面的命令将Elastic Agent安装为服务，将其注册到与指定令牌关联的代理策略中，并启动服务。

```
sudo elastic-agent install -f --url=https://192.0.2.1:8220 \
  --enrollment-token=<string> \
  --certificate-authorities=/path/to/ca.crt
```





https://www.elastic.co/cn/subscriptions

https://www.elastic.co/guide/en/fleet/7.17/add-a-fleet-server.html