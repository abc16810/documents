默认情况下，ES集群没有增加安全策略，导致数据可能被可以路由的到的请求随意访问，为了ES数据安全，一般来说我们的ES如果运行在内网，相对来说是比较安全的。为了保证Elasticsearch数据安全，我们需要对ES进行鉴权。

Elasticsearch鉴权方式选择

- 使用nginx 配置转发
- X-pack认证方式 （文件和原生身份验证，基于角色的访问控制，基于角色的访问控制）
- shield权限管理(收费)
- Realm(收费)

Nginx转发需要额外引入nginx，相当于在ES应用上层进行处理，不考虑，shield是商业软件，需要收费，只可以免费30天，也不考虑，我们选择了X-pack认证方式，使用ES自带的工具组件来完成对Elasticsearch集群的安全访问，X-pack普通用户认证功能永久免费（基于LDAP/kerbors/SAML/AD等认证收费）



### 认证

#### 集群开启鉴权

您可以启用Elasticsearch安全特性，然后为内置用户创建密码。稍后可以添加更多用户，但是使用内置用户可以简化为集群启用安全性的过程。

- 每个节点上启用X-pack安全配置。 打开Elasticsearch根目录下config/elasticsearch.yml文件，将`xpack.security.enabled`值改为true，默认ES是关闭X-pack安全配置的

- 配置CA。节点之间的TLS是防止未授权节点访问您的集群的基本安全设置

  ```
  # 在任何单个节点上，使用elasticsearch-certutil工具为集群生成CA。
  elasticsearch-certutil ca # 生成CA证书；执行过程中需要输入CA的密码和输出文件，直接回车 输入CA密码，输出文件位置为当前位置elastic-stack-ca.p12
  elasticsearch-certutil cert --ca elastic-stack-ca.p12 # 为集群中的节点生成一个证书和私钥。执行完之后证书和私钥将会生成在elastic-certificates.p12文件中
  # 在集群中的每个节点上，复制弹性证书。将elastic-certificates.p12文件拷贝到“$ES_PATH_CONF”目录下
  ```

  ```
  # 集群中的每个节点配置如下
  - xpack.security.enabled=true
  - xpack.security.transport.ssl.enabled=true  # 集群下开启基本验证xpach时必须同时开启ssl，处理集群中节点之间的所有内部通信 
  - xpack.security.transport.ssl.verification_mode=certificate  # 证书验证模式
  - xpack.security.transport.ssl.client_authentication=required  # 必须
  - xpack.security.transport.ssl.keystore.path=elastic-certificates.p12
  - xpack.security.transport.ssl.truststore.path=elastic-certificates.p12
  ```

  如果在创建节点证书时输入了密码，执行以下命令将密码保存在Elasticsearch密钥库中

  ```
  elasticsearch-keystore add xpack.security.transport.ssl.keystore.secure_password
  elasticsearch-keystore add xpack.security.transport.ssl.truststore.secure_password
  ```

- 重启所有节点，成功启动后，浏览器访问`http://ip:9200`  会提示输入用户名和密码

- 为ES内置用户生成密码

  ```
  # 一种是手动一个个用户输入密码，一是通过默认方式自动生成密码。
  elasticsearch-setup-passwords interactive  
  或者
  elasticsearch-setup-passwords auto
  # 两种方式分别对内置用户：elastic、apm_system、kibana、logstash_system、beats_system、remote_monitoring_user，设置了密码
  ```

#### https传输

- 生成证书

  ```
  elasticsearch-certutil  http  # 按照说明下一步生成http.p12证书
  # elasticsearch-certutil cert --ca /certs/elastic-stack-ca.p12 --ca-pass xx --pass xx  -s --out http.p12
  # openssl pkcs12 -in http.p12 -out ca.crt  -clcerts -nokeys 可以导出客户端证书
  ```

- 配置

  ```
  - xpack.security.http.ssl.enabled=true
  - xpack.security.http.ssl.keystore.path=http.p12
  ```

- 如果在创建节点证书时输入了密码，执行以下命令将密码保存在Elasticsearch密钥库中

  ```
  elasticsearch-keystore add xpack.security.http.ssl.keystore.secure_password
  ```

- https 访问

  ```
  https://instance:9200/
  ```

- pem格式证书

  ```
  - xpack.security.http.ssl.enabled=true
  - xpack.security.http.ssl.key=$CERTS_DIR/es01/es01.key
  - xpack.security.http.ssl.certificate=$CERTS_DIR/es01/es01.crt
  - xpack.security.http.ssl.key_passphrase=xxxx # 指定key 密码 不安全模式
  ```

  

使用SSL证书API验证Elasticsearch是否加载了新的密钥存储库

```
GET /_ssl/certificates
```



#### 基于文件的用户身份验证

您可以使用内置的文件域管理和验证用户。使用文件区域，用户在集群中每个节点的本地文件中定义。

责任确保在集群中的每个节点上定义相同的用户。Elastic Stack安全特性没有提供任何机制来保证这一点。不能通过用户api在文件区域中添加或管理用户，也不能在Kibana的管理/安全/用户页面中添加或管理用户。每个节点只能定义一个文件区域。

`file realm `用户的所有数据存储在集群中每个节点上的两个文件中users和users_roles。这两个文件都位于ES_PATH_CONF中，并在启动时读取。users和users_roles文件由节点本地管理，不由集群全局管理。这意味着对于典型的多节点集群，需要对集群中的每个节点应用完全相同的更改。更安全的方法是在一个节点上应用更改，并将文件分发或复制到集群中的所有其他节点，如ansible，puppet等

 配置一个文件realm

- 编辑`elasticsearch.yml`增加如下配置

  ```
  xpack.security.authc.realms.file.file1.order=0 # 0表示首先检查
  ```

- 重启ES

- 在集群中每个节点的ES_PATH_CONF/users文件中添加用户信息

  用户文件存储所有用户及其密码。文件中的每一行都表示一个用户，由用户名、经过散列处理和加盐处理的密码组成

  ```
  elasticsearch-users useradd myadmin -p xxx  -s   # 增加一个用户
  ```

- 在集群中每个节点的ES_PATH_CONF/users_roles文件中添加角色信息

  ```
  elasticsearch-users roles -a superuser  myadmin  # 将myadmin用户设置为管理员
  ```

默认情况下，Elasticsearch每5秒检查这些文件的更改。您可以通过更改elasticsearch中的`resource.reload.interval.high`设置来更改此默认行为

浏览器访问`https://ip:9200`  输入myadmin和密码 登录成功

#### 服务账户

弹性堆栈的安全特性提供了专门用于与连接到弹性搜索的外部服务(如Fleet服务器)集成的服务帐户。服务帐户拥有一组固定的特权，在为它们创建服务帐户令牌之前无法进行身份验证。此外，服务帐户是在代码中预定义的，并且始终是启用的。

服务帐户对应于特定的外部服务。您可以为服务帐户创建服务帐户令牌。然后，服务可以使用令牌进行身份验证

可以为同一个服务帐户创建多个服务令牌，这将防止同一外部服务的多个实例之间共享凭据。每个实例在使用自己独特的服务令牌进行身份验证时可以假定相同的身份

与内置用户相比，服务帐户提供了灵活性，因为它们

- 不要依赖内部本机域，也不总是需要依赖.security索引
- 使用以服务帐户主体命名的角色描述符，而不是传统角色
- 通过服务账户令牌支持多个凭据

服务帐户有一个惟一的主体，其格式为`<namespace>/<service>`，其中名称空间是服务帐户的顶级分组，而服务是服务的名称，并且在其名称空间中必须惟一

服务帐户令牌或服务令牌是服务使用Elasticsearch进行身份验证时使用的惟一字符串。对于给定的服务帐户，每个令牌必须有唯一的名称。由于令牌包含访问凭据，因此使用令牌的客户端应该始终对它们保密

服务令牌可以由service_tokens文件或.security索引支持。您可以为单个服务帐户创建多个服务令牌，这使得相同服务的多个实例可以使用不同的凭据运行

服务令牌永远不会过期。如果不再需要，您必须主动删除它们

```
elasticsearch-service-tokens create elastic/fleet-server my-token   # 创建
SERVICE_TOKEN elastic/fleet-server/my-token = AAEAAWV...OENrT3c
# 使用在Elasticsearch集群中进行身份验证
curl -H "Authorization: Bearer AA..3c" http://localhost:9200/_cluster/health
# 查看
elasticsearch-service-tokens list
# 删除
elasticsearch-service-tokens delete elastic/fleet-server my-token
```



#### 内部本地域

管理和认证用户的最简单方法是使用内部本机域。您可以使用REST api或Kibana添加和删除用户、分配用户角色和管理用户密码

`native` (本地域)验证 与基于文件的验证配置相同，并且在Elasticsearch节点上只能配置一个本机域。不同之处在于本地域可以通过用户API管理用户

将用户存储在专用Elasticsearch索引中的内部域。此领域支持用户名和密码形式的身份验证令牌，在没有显式配置领域的情况下默认启用

- 配置`elasticsearch.yml` 增加如下

  ```
  xpack.security.authc.realms.native.native1.order=1 # 0表示首先检查
  ```

- 重启ES



#### 启用匿名访问

如果不能从传入请求中提取身份验证令牌，则认为传入请求是匿名的。默认情况下，匿名请求被拒绝，并返回一个身份验证错误(状态码401)

要启用匿名访问，需要在elasticsearch.yml配置文件中为匿名用户分配一个或多个角色。例如，配置匿名用户role1和role2

```
xpack.security.authc:
  anonymous:
    username: anonymous_user   # 如果不指定默认_es_anonymous_user
    roles: role1, role2   # 与匿名用户关联的角色。如果没有指定角色，匿名访问将被禁用
    authz_exception: true  # 当为true时，如果匿名用户没有执行请求操作所需的权限，并且不会提示用户提供访问请求资源的凭据，则返回403 HTTP状态码  默认true
```



#### 用户缓存

用户凭据被缓存在每个节点的内存中，以避免连接到远程身份验证服务或为每个传入请求访问磁盘。可以使用该缓存配置用户缓存的特征

缓存的用户凭据在内存中进行哈希处理。默认情况下，Elasticsearch安全特性使用经过改进的sha-256哈希算法。可以通过设置缓存来使用不同的哈希算法

可以使用clear cache API强制驱逐缓存用户。例如，以下请求将所有用户从ad1域驱逐

```
$ curl -XPOST 'http://localhost:9200/_security/realm/ad1/_clear_cache'
```



### 授权

Elastic Stack安全特性增加了授权，这是一个确定是否允许传入请求背后的用户执行请求的过程。

#### 基于角色的访问控制

安全特性提供了一种基于角色的访问控制(RBAC)机制，该机制允许您通过将权限分配给角色和将角色分配给用户或组来对用户进行授权，该授权方式免费

 主要的内置角色`_security/role`

- `ingest_admin`  授予管理所有索引模板和所有摄取管道配置的访问权
-  `kibana_system` 授予Kibana系统用户读写Kibana索引、管理索引模板和令牌以及检查Elasticsearch集群的可用性所必需的访问权限
-  `kibana_admin` 授予访问Kibana的所有功能
-  `monitoring_user` 授予X-Pack监视的任何用户所需的最低权限，而不是使用Kibana所需的权限。这个角色授予对监视索引的访问权，并授予读取基本集群信息所需的特权。这个角色还包括Elastic Stack监控特性的所有Kibana特权。监视用户还应该被分配kibana_admin角色，或者具有访问Kibana实例权限的其他角色
-  `superuser` 授予对集群的完全访问权限，包括所有索引和数据。
-  `watcher_admin` 允许用户创建和执行所有的监视器操作。授予对.watches索引的读访问权

在许多情况下，仅对用户进行身份验证是不够的。您还需要一种方法来控制用户可以访问哪些数据以及他们可以执行哪些任务。通过启用Elasticsearch安全特性，您可以通过将访问权限分配给角色并将这些角色分配给用户来对用户进行授权。使用这种基于角色的访问控制机制(RBAC)，可以限制用户kandorra只对事件索引执行读操作，限制对所有其他索引的访问

创建角色

- 通过api`POST /_security/role/xxx`
- 通过本地文件`roles.yml`



#### 启用审计日志

```
xpack.security.audit.enabled=true  # 默认false
```

