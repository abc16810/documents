#### 简介

优化的HTTP / 1.x, HTTP / 2服务器

高性能 HTTP 服务器。相较于传统 Web 服务器，它充分利用了 HTTP/2 的资源加载优先级和服务器推送技术，所以在静态文件方面性能明显优于 Nginx 服务器

**特性**

- HTTP/1.0, HTTP/1.1
- HTTP/2: 完全支持依赖和基于权重的服务端调整优先级, 支持缓存服务推送
- TCP快速打开
- TLS: 会话恢复(独立和缓存)，带有自动键翻转的会话票据，自动OCSP装订，正向加密和快速AEDE运算，特权分离的私钥保护
- 静态文件服务
- FastCGI
- reverse proxy  反向代理
- 使用mruby(基于机架)编写脚本
- 基于bpf的跟踪工具(实验)

#### 安装

```
# https://github.com/tatsushid/h2o-rpm
yum install h2o-2.2.6-1.el6.x86_64.rpm
# docker https://hub.docker.com/r/lkwg82/h2o-http2-server/
docker run -p "8080:8080" -ti lkwg82/h2o-http2-server
```

#### 配置

快速开始配置文件`h2o.conf` 。 H2O使用YAML 1.1作为其配置文件的语法

```
listen:
  port: 8080   # 监听8080端口
user: nobody   # 启动用户
hosts:
  "myhost.example.com":
    paths:
      "/":                               # 类似nignx location / {}
        file.dir: /path/to/the/public-files   # 服务文件
      "/assets":                 # 当请求路径为/assets 类似nginx中的location ^~/assets/ {}
        file.dir: /path/to/asset-files
access-log: /path/to/the/access-log    # 日志
error-log: /path/to/the/error-log
pid-file: /path/to/the/pid-file
```

启动

```
h2o -m daemon -c h2o.conf
```

停止

```
sudo kill -TERM `cat /path/to/the/pid-file`
```



#### 其它配置

- 同时监听HTTP和HTTPS

  ```
  hosts:
    "www.example.com":
      listen:
        port: 80
      listen:
        port: 443
        ssl:
          certificate-file: /path/to/server-certificate.crt
          key-file:         /path/to/private-key.crt
      paths:
        "/":
          file.dir: /path/to/doc-root
  
  access-log: /path/to/the/access-log
  error-log: /path/to/the/error-log
  pid-file: /path/to/the/pid-file
  http2-reprioritize-blocking-assets: ON   # performance tuning option
  ```

- 将HTTP重定向到HTTPS

  ```
  hosts:
    "www.example.com:80":
      listen:
        port: 80
      paths:
        "/":
          redirect: localhost:443
    "www.example.com:443":
      listen:
        port: 443
        ssl:
          certificate-file: /path/to/server-certificate.crt
          key-file:         /path/to/private-key.crt
      paths:
        "/":
          file.dir: /path/to/doc-root
  
  access-log: /path/to/the/access-log
  error-log: /path/to/the/error-log
  pid-file: /path/to/the/pid-file
  http2-reprioritize-blocking-assets: ON   # performance tuning option
  ```

- 反向代理

  ```
  hosts:
    "www.example.com":
      listen:
        port: 80
      paths:
        "/":
          proxy.reverse.url: https://127.0.0.1:8080/
          # proxy.preserve-host: ON    # to not rewrite the incoming host:port
          # proxy.timeout.keepalive: 0 # to explicitly disable persistent connections to the application server
        "/assets":                     # serve asset files directly
          file.dir: /path/to/asset-files
  
  access-log: /path/to/the/access-log
  error-log: /path/to/the/error-log
  pid-file: /path/to/the/pid-file
  http2-reprioritize-blocking-assets: ON # performance tuning option
  ```

  If you are getting 400 Bad Request: malformed Host header, add proxy.preserve-host: ON

**[官网](https://h2o.examp1e.net/index.html)**