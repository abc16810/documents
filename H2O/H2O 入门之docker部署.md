#### 部署

```
docker pull lkwg82/h2o-http2-server
```

默认配置文件为`/home/h2o/h2o.conf`,  默认的工作目录为/home/h2o

```
hosts:
  default:
    listen:
      port: 8080
    paths:
      /:
        file.dir: /var/www/html
        file.dirlisting: ON

access-log: /dev/stdout
error-log: /dev/stderr
```

上述默认情况下，没有/var/www/html 目录，当docker run 启动容器后，测试会发现not found，我们通过docker-compose.yml 编排自定义相关配置和目录如下

自定义配置文件`h2o.conf ` , 并指定工作目录为`/etc/h2o`

```
version: '3'

services:
  h2o:
    image: lkwg82/h2o-http2-server:v2.2.6
    command: ["h2o", "--conf", "/etc/h2o/h2o.conf"]
    working_dir: /etc/h2o
    ports:
       - "8080:8080"
    volumes:
       - "./conf:/etc/h2o/:ro"
       - "./html:/var/www/html:ro"
       - "logsvolume:/home/h2o"
    restart: always

volumes:
  logsvolume:
```

`conf/h2o.conf`

```
max-connections: 2000
limit-request-body: 10240000
send-server-name: OFF
compress: ON  # 动态压缩
compress-minimum-size: 100
access-log:
    path: /home/h2o/access-log
    format: "%h %l %u %t \"%r\" %s %b \"%{Referer}i\" \"%{User-agent}i\" \"%{X_forwarded_for}i\""
    escape: apache
error-log: /home/h2o/error-log
error-doc:
  - status: 404
    url: /404.html
  - status: [500, 502, 503, 504]
    url: /50x.html

listen:
  port: 8080   # 监听8080端口
hosts:
  "myhost.example.com":
    paths:
      "/":                               
        file.dir: /var/www/html
```

**启动**

```
docker-compose up
```























https://github.com/lkwg82/h2o.docker

https://hub.docker.com/r/lkwg82/h2o-http2-server