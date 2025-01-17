#### 语法

H2O使用YAML 1.1作为其配置文件的语法。

**配置级别**

在使用H2O的配置指令时，重要的是要理解有四个配置级别:全局、主机、路径、扩展

- Global-level： 配置会影响整个服务器
- Host-level : 主机级配置影响特定主机名的配置(即对应于Apache HTTP服务器的<VirtualHost>指令
- Path-level: 路径级配置只影响特定于路径的资源的行为。
- Extension-level: 配置影响具有某些扩展名的文件的服务方式

某些配置指令可以在多个级别中使用。例如，`listen`既可以在全局级别使用，也可以在主机级别使用。`expires`可以在所有级别使用。另一方面，文件。`dir`只能在路径级使用

**Path-level 配置**

```
    ...
    paths:
      "/":
        file.dir: /path/to/doc-root
        fastcgi.connect:
          port: /path/to/fcgi.sock
          type: unix
   # 从2.1版本开始，还可以将路径级配置定义为一个映射序列，而不是单个映射
    paths:
      "/":
        - file.dir: /path/to/doc-root
        - fastcgi.connect:
            port: /path/to/fcgi.sock
            type: unix
```

当收到`https://daenmo.com/foo`的请求时，首先执行文件处理程序，尝试将名为`/path/to/doc-root/foo`的文件作为响应。如果文件不存在，则调用FastCGI处理程序

**使用YAML别名**

在处理配置文件之前，H2O会先解析YAML别名。因此，可以使用别名来减少配置文件的冗余

```
hosts:
  "example.com":
    listen:
      port: 443
      ssl:
        certificate-file: /path/to/example.com.crt
        key-file:         /path/to/example.com.crt
    paths: &default_paths
      "/":
        file.dir: /path/to/doc-root
  "example.org":
    listen:
      port: 443
      ssl:
		...
    paths: *default_paths  # 通过别名重用路径    
```

**使用YAML合并**

从2.0版本开始，H2O可以识别YAML1.1版本的Merge Key Language-Independent类型。用户可以使用该特性将一个现有映射与另一个映射合并

```
hosts:
  "example.com":
    listen:
      port: 443
      ssl: &default_ssl
        minimum-version: TLSv1.2
        cipher-suite: ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256
        certificate-file: /path/to/example.com.crt
        key-file:         /path/to/example.com.crt
    paths:
      ...
  "example.org":
    listen:
      port: 443
      ssl:
        <<: *default_ssl
        certificate-file: /path/to/example.org.crt
        key-file:         /path/to/example.org.crt
    paths:
      ...
```

**包含文件**

从2.1版开始，可以使用!file自定义YAML标记从配置文件中包含一个YAML文件

```
hosts:
  "example.com":
    listen:
      port: 443
      ssl: !file default_ssl.conf
    paths:
      ...
  "example.org":
    listen:
      port: 443
      ssl:
        <<: !file default_ssl.conf
        certificate-file: /path/to/example.org.crt  # 重写文件中定义的
        key-file:         /path/to/example.org.crt
    paths:
      ...
```

**引入变量**

从2.3版开始，可以使用!env自定义YAML标记在配置文件中引用环境变量(被解释为标量)

```
hosts:
  "example.com":
    listen:
      port: !env H2O_PORT
    paths:
      ...
```

#### 配置指令

- hosts   将主机:端口映射到每台主机配置的映射。该指令是强制性的，必须至少包含一个， 可以使用*通配符。精确匹配优于使用通配符。 全局级别

- paths  路径及其构型的映射，使用prefix-match搜索映射。当发现多个匹配路径时，选择路径最长的条目， 没有发现，返回 Not found 。 主机级别

- listen 指定服务器应该监听的端口，除了指定端口号外，还可以指定绑定地址或SSL配置。(全局级别,主机级别)

  ```
  # accept HTTP on port 80 on default address (both IPv4 and IPv6)
  listen: 80
  
  # accept HTTP on 127.0.0.1:8080
  listen:
    host: 127.0.0.1
    port: 8080
  
  # accept HTTPS on port 443
  listen:
    port: 443
    ssl:
      key-file: /path/to/key-file
      certificate-file: /path/to/certificate-file
  
  # accept HTTPS on port 443 (using PROXY protocol)
  listen:
    port: 443
    ssl:
      key-file: /path/to/key-file
      certificate-file: /path/to/certificate-file
    proxy-protocol: ON
  ```



**全局级别**

- access-log 置访问日志的路径和格式(可选) 默认格式`%h %l %u %t "%r" %s %b "%{Referer}i" "%{User-agent}i"`

  ```
  access-log:
      path: /path/to/access-log-file
      format: "%h %l %u %t \"%r\" %s %b \"%{Referer}i\" \"%{User-agent}i\" \"%{X_forwarded_for}i\""  
      escape: apache
  # https://h2o.examp1e.net/configure/access_log_directives.html
  ```

- error-log  错误日志输出，默认`/dev/stderr`。如果该路径以|开头，则将该路径的其余部分视为一个命令，日志应该通过管道传递到该命令。 全局级别

  ```
  error-log: "| rotatelogs /path/to/error-log-file.%Y%m%d 86400"
  ```

- handshake-timeout  连接在准备好接受HTTP请求之前所花费的最大时间(以秒为单位)  默认10  

- limit-request-body   请求体的最大大小(以字节为单位)(例如POST的内容)  默认1073741824 (1GB) 

- max-connections  处理的最大连接数  默认1024 

- max-delegations 限制委托的数量(即使用`X-Reproxy-URL`头的内部重定向)  默认5

- num-name-resolution-threads 为名称解析而运行的最大线程数 默认32 

- num-ocsp-updaters OCSP更新器的最大数目 默认10 

- num-threads 工作线程数  默认值是通过`getconf NPROCESSORS_ONLN`获取的连接到系统的处理器数量。

- pid-file  服务器的进程id应该写入的文件的名称 ，默认none

- tcp-fastopen 用于TCP Fast Open的队列大小。TCP Fast Open是对TCP/IP协议的扩展，它可以减少建立连接的时间。在支持该特性的Linux上，默认值为4,096。在其他平台上，默认值为0(禁用)

- send-server-name  一个布尔标记(ON或OFF)，指示是否应该发送服务器响应头  默认ON 设置为OFF伪装

- server-name 让用户重写服务器响应头的值， 默认为`h2o/VERSION-NUMBER`

- send-informational  指定H2O可以发送1xx信息响应的客户端协议。 默认值`except-h1`

- ssl-session-resumption 配置基于缓存和基于票证的会话恢复。为了减少TLS (SSL)握手引入的延迟，Internet Engineering Task Force定义了两种方法来恢复以前的加密会话。H2O支持两种方式:基于缓存的会话恢复(定义在RFC 5246)和基于票据的会话恢复(定义在RFC 5077)。  默认 `mode 为all` 将同时使用基于会话和基于票据的恢复，对于支持这两种方法的客户端，优先使用基于票据的恢复。

  ```
  # use both methods (storing data on internal memory)
  ssl-session-resumption:
      mode: all
  
  # use both methods (storing data on memcached running at 192.168.0.4:11211)
  ssl-session-resumption:
      mode: all
      cache-store: memcached
      ticket-store: memcached
      cache-memcached-num-threads: 8
      memcached:
          host: 192.168.0.4
          port: 11211
  
  # use ticket-based resumption only (with secrets used for encrypting the tickets stored in a file)
  ssl-session-resumption:
      mode: ticket
      ticket-store: file
      ticket-file: /path/to/ticket-encryption-key.yaml
  ```

- temp-buffer-path 创建临时缓冲区文件的目录。H2O使用一个叫做h2o_buffer_t的内部结构来缓冲各种数据(例如POST内容，来自上游HTTP或FastCGI服务器的响应)。当缓冲区中分配的数据量超过默认值32MB时，它就开始从指令指向的目录中分配存储空间。可以使用`temp-buffer-threshold`指令来调整或禁用这个阈值，默认`/tmp`

- temp-buffer-threshold  将大内存分配分配到临时缓冲区的最小大小。最小值为`1MB(1048576)` 默认`32M（33554432）`

- user  启动用户， 如果省略该指令，并且服务器是在root权限下启动的，则服务器将尝试将setuid设置为nobody

- crash-handler  脚本调用，如果h2o收到一个致命的信号 默认

  ```
  crash-handler: "${H2O_ROOT}/share/h2o/annotate-backtrace-symbols"
  ```

- crash-handler.wait-pipe-close h2o是否应该在退出之前等待崩溃处理程序管道关闭 默认OFF

- http1-request-timeout  请求超时时间  默认10   HTTP/1协议

- http1-request-io-timeout   输入请求I/O超时时间(以秒为单位)  默认5

- http1-upgrade-to-http2  指示是否允许升级到HTTP/2  默认ON

- 

**所有级别**

- stash 指令用于存储可重用的YAML变量。这个指令本身什么都不做，但可以用来存储YAML变量，并使用YAML别名重用这些变量

  ```
  stash:
    ssl: &ssl
      port: 443
    paths: &paths
      /:
        file.dir: /path/to/root
  hosts:
    "example.com":
      listen:
        <<: &ssl
        ssl:
          certificate-file: /path/to/example.com.crt
          key-file:         /path/to/example.com.key
      paths: *paths
    "example.org":
      listen:
        <<: &ssl
        ssl:
          certificate-file: /path/to/example.org.crt
          key-file:         /path/to/example.org.key
      paths: *paths
  ```

  

- setenv 设置一个或多个环境变量。环境变量是一组包含任意字符串的键值对，可以从独立服务器调用的应用程序(例如fastcgi处理程序，mruby处理程序)和访问日志程序中读取

  ```
  setenv:
    FOO: "value_of_FOO"
  ```

- unsetenv 取消设置一个或多个环境变量

  ```
  hosts:
    example.com:
      setenv:
        FOO: "value_of_FOO"
      paths:
        /specific-path:  #排除/specific-path 路径下
          unsetenv:
            - FOO
        ...
  ```

- compress 启用HTTP响应的动态压缩  默认OFF

  ```
  # enable all algorithms
  compress: ON
  
  # enable by name
  compress: [ gzip, br ]
  
  # enable gzip only
  compress: [ gzip ]
  ```

- compress-minimum-size  压缩最小阈值  默认100

- gzip   启用使用gzip压缩  默认OFF

- error-doc  指定返回错误响应(即带有4xx或5xx状态码的响应)   类似nginx 的`error_page`

  ```
  error-doc:
    status: 404
    url: /404.html
  error-doc:
    - status: 500
      url: /internal-error.html
    - status: 503
      url: /service-unavailable.html
  error-doc:
    status: [500, 502, 503, 504]
    url: /50x.html
  ```

- expires 有效期

  ```
  expires: 1 day  # Cache-Control: max-age=86400
  ```

**file** 用于指定静态文件路径

- file.custom-handler  该指令将扩展映射到一个自定义处理器(例如FastCGI)。

  ```
  file.custom-handler:
    extension: .php
    fastcgi.connect:
      port: /tmp/fcgi.sock
      type: unix
  ```

- file.dir 指定静态文件路径  path级别

- file.dirlisting 指定在索引文件不存在的情况下是否发送目录列表  默认OFF   类似nginx的autoindex

- file.etag  指定是否发送标签  默认ON

- file.file 将路径映射到特定的文件 path级别

  ```
  paths:
    /robots.txt:
      file.file: /path/to/robots.txt
  ```

- file.index  指定默认首页

  ```
  file.index: [ 'index.html', 'index.htm', 'index.txt' ]  # 默认
  ```

- file.mime.addtypes 通过添加指定的MIME类型映射来修改MIME映射

  ```
  file.mime.addtypes:
      "application/javascript": ".js"
      "image/jpeg": [ ".jpg", ".jpeg" ]
  ```

- file.mime.removetypes  移除作为扩展序列提供的指定扩展的MIME映射

- file.mime.setdefaulttype 置当扩展不存在于MIME映射中时使用的默认MIME类型

  ```
  file.mime.setdefaulttype: "application/octet-stream"  
  ```

- file.mime.settypes 将MIME映射重置为给定映射

  ```
  file.mime.settypes:
      "text/html":  [ ".html", ".htm" ]
      "text/plain": ".txt"
  ```

- file.send-compressed  一种标志，指示应如何提供预压缩文件  默认OFF



**其它**

- redirect 将请求重定向到给定的URL

  ```
  hosts:
      "example.com:80":
          paths:
              "/":
                  redirect:
                      status: 301
                      url:    "https://example.com/"
  ```

  