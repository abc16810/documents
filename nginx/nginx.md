Nginx作为一个非常流行和成熟的Web Server和Reserve Proxy Server，网上有大量的性能优化教程，但是不同的业务场景千差万别，什么配置是最适合自己的，需要大量的测试和实践以及不断的优化改进。

#### 安装

docker 安装 或者Centos上`yum install nginx -y`

#### 相关命令

```
nginx -s reload  # 向主进程发送信号，重新加载配置文件，热重启
nginx -s reopen   # 重启 Nginx
nginx -s stop    # 快速关闭
nginx -s quit    # 等待工作进程处理完成后关闭
nginx -T         # 查看当前 Nginx 最终的配置
nginx -t         # 检查配置是否有问
```

### 配置

#### main配置（全局配置，对全局生效）

载入动态模块
```
load_module  modules/ngx_http_js_module.so;
```

指定启动用户和组 
```
user  nginx;   # 指定启动用户
user  nginx nginx;
```

指定 Nginx 启动的 worker 子进程数量
```
worker_processes: auto  # 与当前cpu物理核心数一致
worker_processes 4; # 指定具体子进程数量
```

将每个 worker 子进程与我们的 cpu 物理核心绑定
```
worker_cpu_affinity auto;
worker_cpu_affinity 01 10;
worker_cpu_affinity 0101 1010;
# worker_cpu_affinity 01 10;表示开启两个进程，第一个进程对应着第一个CPU内核，第二个进程对应着第二个CPU内核
# 2核是 01，四核是0001，8核是00000001，有多少个核，就有几位数，1表示该内核开启，0表示该内核关闭。
```

指定 worker 子进程的 nice 值，以调整运行 Nginx 的优先级，通常设定为负值，以优先调用 Nginx
```
worker_priority -10; # 120-10=110，110就是最终的优先级
# Linux 默认进程的优先级值是120，值越小越优先；nice 定范围为 -20 到 +19
```

指定 worker 子进程可以打开的最大文件句柄数
```
worker_rlimit_nofile 65535;
```

指定 worker 子进程优雅退出时的超时时间，一旦超过这个时间，nginx会试图关闭目前所有仍然打开的tcp连接
```
worker_shutdown_timeout 5s; 
```

指定Nginx 的错误日志存放及级别
```
error_log  /var/log/nginx/error.log warn;
error_log  /var/log/nginx/error.log notice;
# level是日志级别；debug,info,notice,warn,error,crit,alert,emerg，从左到右，依次增大
```

Nginx 服务启动时的 pid 存放位置
```
pid   /var/run/nginx.pid;
```

以守护进程方式运行Nginx (默认)
```
daemon on;  # off
```

处理几个特殊的调试点(通常不会用这个配置项, 默认无) 
```
debug_points [stop|abort] 
```

定义变量
```
env PERL5LIB;
# env VAR|VAR=VALUE
```

nginx使用锁的机制来实现accept_mutex功能和共享内存，大多数操作系统中锁都是一个原子操作，这种情况下这条指令无效，还有一些操作系统中使用“锁文件”的的机制来实现锁，此命令用来指定锁文件前缀名
```
lock_file logs/nginx.lock;  # 默认
```

当设置为on，Ningx将会开启多个进程，包括一个主进程（master进程）和多个worker进程。如果设置为off，则Nngix将以master进程来运行
```
master_process on;  # 默认
```

在解析配置文件时对正则表达式启用或禁用实时编译（PCRE JIT）
```
pcre_jit on | off;   # 默认off （RCRE JIT能显著提升正则表达式的处理速度。）
```

指定ssl引擎
```
ssl_engine engine # 默认无
# 如果使用了硬件ssl加速设备，使用此指令指定
```

定义线程池，在使用异步IO的情况下，定义命名线程池，并设置线程池大小和等待队列大小。当线程池中所有线程都繁忙时，新任务会放在等待队列中，如果等待队列满了，任务会报错退出。命名线程池可以定义多个，供http模块的异步线程指令（aio）调用
```
thread_pool default threads=32 max_queue=65535;  # 默认（v1.7.11）
```

设置时间精度，减少worker进程调用系统时间函数的次数。默认情况下，每个核心事件都会调用gettimeofday()接口来获得系统时间，以便nginx计算连接超时等工作，此指令指定更新时间的间隔，nginx在间隔时间内只调用一次系统时间函数
```
timer_resolution 1s;
```

指定默认工作路径。主要用于worker进程导出内存转储文件
```
working_directory /etc/nginx;
```

#### event

 配置影响 Nginx 服务器与用户的网络连接
```
events {
 ...
}
```

当启用这个参数时，会使用互斥锁交替给worker进程分配新连接，否则话所有worker进程会争抢新连接，即或造成所谓的“惊群问题”，惊群问题会使nginx的空闲worker进程无法进入休眠状态，造成系统资源占用过多。启用此参数会一定程度上导致后台服务器负载不均衡，但是在高并发的情况下，关闭此参数可以提高nginx的吞吐量。
```
accept_mutex off;   # 默认
```

如果accept_mutex参数启用，当一个空闲worker进程尝试获取互斥锁时发现有另一个worker进程已经获得互斥锁并处理新连接，这个空闲的worker进程等待下一次获取互斥锁尝试的时间。而获得互斥锁的进程在处理完当前连接后，会立即尝试获取互斥锁，因此此数值较大或连接压力较小时，会造成部分worker进程总是空闲，一部分进程总是繁忙的情况
```
accept_mutex_delay 500ms; # 默认
```

需要debug模块支持，需确认安装时包括了debug模块，可以使用nginx -V命令确定包含--wih-debug参数。

对特定的客户发起的连接开启debugging级别日志，用于分析和拍错。可以指定IPv4或者IPv6地址（v1.3.0,v1.2.1）或一个无类网段或域名，或UNIX socket（v1.3.0,v1.2.1）
```
debug_connection localhost;
debug_connection 127.0.0.1;
# debug_connection address | network | unix:;
# 非指定连接的日志级别依然由error_log指令决定
```

当设置为off时，一个worker进程获得互斥锁时一次只处理一个新连接，如果设置为on，则一次性将所有新连接都分配给获得当前互斥锁的worker进程、当使用kqueue连接处理方式时（use kqueue），此项指令无效
```
multi_accept off;   # 默认
```

指定连接处理方式，通常不需要指定，nginx会自动使用最有效的方式
```
use  epoll;  默认无
```

在v1.1.4和1.0.7中出现。当启用aio（异步IO）和epoll连接处理方式后，单个worker进程最大的未完成异步IO操作数。
```
worker_aio_requests 32; # 默认
```

指定单个worker进程可处理的最大并发连接数限制。

这个连接数包括和后台服务器之间的连接在内的所有的连接，而不仅是与客户的连接。所有worker进程的总连接数（即worker_connections × worker_processes）不能超过操作系统最大可打开句柄数的限制（nofile），nofile限制可以通过`worker_rlimit_nofile`指令修改。
```
worker_connections 1024;  # 默认512
```

#### http

配置代理，缓存，日志定义, 代理等 （有些配置同样适用于`server`, `location`）

```
include         /etc/nginx/mime.types;  # 文件扩展名与类型映射表
default_type    text/plain ;  # 默认文件类型  （application/octet-stream 任意类型的二进制流数据）
# 指定日志记录格式
log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
access_log  /var/log/nginx/access.log  main;  #  Nginx访问日志存放位置
sendfile        on; # Sendfile 是 Linux2.0 以后的推出的一个系统调用，它能简化网络传输过程中的步骤，提高服务器性能
tcp_nopush      on; # 设置数据包会累积一下再一起传输，可以提高一些传输效率。tcp_nopush必须和 sendfile 搭配使用
tcp_nodelay     on; # 小的数据包不等待直接传输。默认为on。看上去是和 tcp_nopush相反的功能，但是两边都为 on 时 nginx 也可以平衡这个功能的使用
server_tokens off;  # 去掉响应中版本信息Server: nginx
send_timeout 300;  服务端向客户端传输数据的超时时间单位秒 默认60s
resolver_timeout 30s;  设置名称解析的超时时间 默认30
postpone_output 1460; 客户端数据的传输将被推迟，设置为0，禁用延迟数据传输，只是会将响应header立刻发送至client
```


**keepalive**
```
keepalive_disable none| browser ...;  #  禁用与行为不端的浏览器的保持连接 默认msie6  none表示启用与所有浏览器的保持连接
keepalive_requests 1000;   # keepalive_requests指令用于设置一个keep-alive连接上可以服务的请求的最大数量，当最大请求数量达到时，连接被关闭。1.19.10版本默认是100， 之后版本默认是1000。这个参数的真实含义，是指一个keep alive建立之后，nginx就会为这个连接设置一个计数器，记录这个keep alive的长连接上已经接收并处理的客户端请求的数量。如果达到这个参数设置的最大值时，则nginx会强行关闭这个长连接，逼迫客户端不得不重新建立新的长连接。
keepalive_time  1h; # 限制通过一个保持活动连接可以处理请求的最长时间。到了这个时间后，在后续的请求处理之后关闭连接 默认1h,(版本 1.19.10)
keepalive_timeout  75s [header_timeout]; # 第一个参数设置一个超时时间，在此期间保持活动的客户端连接将在服务器端保持打开状态 , 0值禁用保持活动客户端连接
```

**client**

```
client_body_buffer_size  8k|16k;  # 设置读取客户端请求正文的缓冲区大小即用来处理POST提交数据，上传文件等。如果请求正文大于缓冲区，则将整个正文或仅其部分写入临时文件。默认情况下，缓冲区大小等于两个内存页。 x86、其他 32 位平台和 x86-64 上的为 8K。在其他 64 位平台上通常为 16K。根据需要调整该值
client_body_temp_path path [level1 [level2 [level3]]];  # 定义一个目录，用于存储保存客户端请求正文的临时文件。  指定目录下最多可以使用三级子目录层次结构如client_body_temp_path /spool/nginx/client_temp 1 2;
client_body_timeout 60s; 该指令设置请求正文即请求体（request body）的读超时时间。超时仅设置为两个连续读取操作之间的时间段，而不是整个请求主体的传输。如果客户端在此时间内未传输任何内容，请求将以408（请求超时）错误终止
client_header_buffer_size 1k; # 设置读取客户端请求标头的缓冲区大小。对于大多数请求，1K 字节的缓冲区就足够了。但是，如果请求包含长 cookie，或者来自 WAP 客户端，则它可能不适合 1K， 通过由 large_client_header_buffers 指令配置
large_client_header_buffers 4 8k;  # 设置用于读取大型客户端请求标头的缓冲区的最大数量和大小
client_header_timeout 60s; # 指定等待client发送一个请求头的超时时间。如果在超时时间内，client没发送任何东西，nginx返回HTTP状态码408(“Request timed out”)
client_max_body_size 1m; # 设置客户端请求正文的最大允许大小。  如果请求中的大小超过配置的值，则会向客户端返回 413（请求实体太大）错误， 设置为0 禁止检查
client_body_in_single_buffer on|off;  确定 nginx 是否应将整个客户端请求正文保存在单个缓冲区中。使用 $request_body 变量时建议使用该指令默认off
client_body_in_file_only on|clean|off; # 确定 nginx 是否应将整个客户端请求正文保存到文件中。  该指令可以在调试期间使用，默认off
```
传输的数据大于client_max_body_size，是传不成功的。小于client_body_buffer_size直接在内存中高效存储。如果大于client_body_buffer_size小于client_max_body_size会存储临时文件，临时文件一定要有权限。如果追求效率，就设置 client_max_body_size client_body_buffer_size相同的值，这样就不会存储临时文件，直接存储在内存了

**error_page**
定义将针对指定错误显示的 URI。  uri 值可以包含变量
```
error_page 404             /404.html;
error_page 500 502 503 504 /50x.html;
error_page 404 =301 http://example.com/notfound.html;
```

**fastcgi**

对于来自 FastCGI Server 的 Response，Nginx 将其缓冲到内存中，然后依次发送到客户端浏览器
```
fastcgi_buffer_size 128k;  #读取fastcgi应答第一部分需要多大缓冲区，该值表示使用1个128kb的缓冲区读取应答第一部分(应答头),可以设置为fastcgi_buffers选项缓冲区大小
fastcgi_buffers 8 128k;  # 控制 nginx 最多创建 8 个大小为 128K 的缓冲区
fastcgi_connect_timeout 300; # 连接到后端fastcgi超时时间，单位秒
fastcgi_send_timeout 300;  # 向fastcgi请求超时时间(这个指定值已经完成两次握手后向fastcgi传送请求的超时时间)
fastcgi_read_timeout 300; # 接收fastcgi应答超时时间，同理也是2次握手后
```

**反向代理**
 
 反向代理一般配置`location` 上下文中
 
`proxy_buffering`开启的情况下，nignx会把后端返回的内容先放到缓冲区当中，然后再返回给客户端(边收边传，不是全部接收完再传给客户端)。 临时文件由`proxy_max_temp_file_size`和`proxy_temp_file_write_size`这两个指令决定的。如果响应内容无法放在内存里边,那么部分内容会被写到磁盘上

`proxy_buffering`关闭，那么nginx会立即把从后端收到的响应内容传送给客户端，每次取的大小为`proxy_buffer_size`的大小

> proxy_buffering启用时，要提防使用的代理缓冲区太大。可能会占用大量内，限制代理能够支持的最大并发连接数

```
proxy_buffering  on;  # 开启后端响应内容的缓冲区  默认on
proxy_buffer_size 4k; # 设置nginx保存用户头部信息的缓冲区大小，该缓冲区大小等于指令 proxy_buffers所设置的，但是可以把它设置得更小， 如果太小，会出现502错误码
proxy_buffers 8 64k;   # 指令设置缓冲区的大小和数量  默认情况下8 4k|8k;
proxy_busy_buffers_size 128k;
proxy_temp_file_write_size 8k;  
proxy_max_temp_file_size 1024m;  
proxy_http_version 1.1; # 代理的 HTTP 协议版本 默认1.0 1.0下有些特性不支持
proxy_next_upstream error timeout http_500# 在哪些情况下（超时，500错误）应将请求传递给upstream中的下一个服务器 如果是(POST, LOCK, PATCH)请求则加上non_idempotent
proxy_pass URL;  # 设置代理服务器的协议和地址以及位置应映射到的可选 URI
 # 不带 / 意味着 Nginx 不会修改用户 URL ，而是直接透传给上游的应用服务器
  location /some/path/ {
    proxy_pass http://127.0.0.1;
  }
 # 带 / 意味着 Nginx 会修改用户 URL ，修改方法是将 location 后的 URL 从用户 URL 中删除
  location /name/ {
    proxy_pass http://127.0.0.1/remote/;
  }

proxy_pass_request_body on; # 指示是否将原始请求body传递给代理服务器 默认on
proxy_pass_request_headers on; 
proxy_read_timeout 60s; # 默认60 从代理服务器读取响应的超时
proxy_send_timeout 60s;  # 请求传输到代理服务器的超时时间
proxy_connect_timeout 60s; # 与代理服务器建立连接的超时时间
proxy_redirect off|default;  # 修改从被代理服务器传来的应答头中的"Location"和"Refresh"字段，off将在这个字段中禁止所有的proxy_redirect指令
proxy_request_buffering on; 启用或禁用客户端请求正文的缓冲。Nginx在读完header的时候，不会立刻连接到 upstream，而是需要在读完client完整的body的后才会继续执行,即与此时才会去和upstream建立连接然后发送数据 默认on

```

`proxy_busy_buffers_size`不是独立的空间，他是proxy_buffers和proxy_buffer_size的一部分。nginx会在没有完全读完后端响应的时候就开始向客户端传送数据，所以它会划出一部分缓冲区来专门向客户端传送数据(这部分的大小是由proxy_busy_buffers_size来控制的，建议为proxy_buffers中单个缓冲区大小的2倍)，然后它继续从后端取数据，缓冲区满了之后就写到磁盘的临时文件中

临时文件由proxy_max_temp_file_size和proxy_temp_file_write_size这两个指令决定
`proxy_temp_file_write_size 256k`  # 当启用缓冲从代理服务器到临时文件的响应时，限制一次写入临时文件的数据大小,默认是proxy_buffer_size和proxy_buffers中设置的缓冲区大小的2倍，Linux下一般是8k。`proxy_max_temp_file_size`设置临时文件的最大大小。默认1024m， 设置为0时, 则直接关闭硬盘缓冲.


- 所有的proxy buffer参数是基于每个请求的，每个请求会安按照参数的配置获得自己的buffer
- proxy_buffers和proxy_busy_buffers_size参数需要proxy_buffering参数开启后才起作用
- 无论proxy_buffering是否开启，proxy_buffer_size都是工作的，proxy_buffer_size所设置的buffer_size的作用是用来存储upstream端response的header。

set header 允许将字段重新定义或附加到传递给代理服务器的请求标头
```
proxy_set_header Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Scheme $scheme;
```


**gzip压缩**

GZIP 是规定的三种标准 HTTP 压缩格式之一。目前绝大多数的网站都在使用 GZIP 传输 HTML 、CSS 、 JavaScript 等资源文件。对于文本文件， GZiP 的效果非常明显，开启后传输所需流量大约会降至 1/4~1/3

```
gzip on;  # 默认off，是否开启gzip
# 要采用 gzip 压缩的 MIME 文件类型，其中 text/html 被系统强制启用；
gzip_types text/plain application/javascript application/x-javascript text/css application/xml text/javascript application/x-httpd-php image/jpeg image/gif image/png;
# 默认 off，该模块启用后，Nginx 首先检查是否存在请求静态文件的 gz 结尾的文件，如果有则直接返回该 .gz 文件内容；
gzip_static off;

# 默认 off，nginx做为反向代理时启用，用于设置启用或禁用从代理服务器上收到相应内容 gzip 压缩；
gzip_proxied any; # 无条件压缩所有结果数据

# 用于在响应消息头中添加 Vary：Accept-Encoding，使代理服务器根据请求头中的 Accept-Encoding 识别是否启用 gzip 压缩；
gzip_vary off;  

# gzip 压缩比，压缩级别是 1-9，1 压缩级别最低，9 最高，级别越高压缩率越大，压缩时间越长；
# 不是压缩级别越高越好，其实gzip_comp_level 1的压缩能力已经够用了，后面级别越高，压缩的比例其实增长不大，反而很吃处理性能
gzip_comp_level 1;

# 获取多少内存用于缓存压缩结果，16 8k 表示以 8k*16 为单位获得；
gzip_buffers 16 8k;

# 允许压缩的页面最小字节数，页面字节数从header头中的 Content-Length 中进行获取。默认值是 0，不管页面多大都压缩。建议设置成大于 1k 的字节数，小于 1k 可能会越压越大；
# gzip_min_length 1k;

# 默认 1.1，启用 gzip 所需的 HTTP 最低版本；
gzip_http_version 1.1;
# 禁用IE 6 gzip
gzip_disable "MSIE [1-6]\.";
```

**缓存**


```
# 配置缓存模块
http {
  ...
  # proxy_cache_path path [level=levels] ...# 可选参数省略  仅在'http'上下文中可用
  proxy_cache_path /tmp/ngx_cache/proxy_cache_dir levels=1:2 keys_zone=mycache:30m inactive=1d max_size=100m;
}
```

- **path** 缓存文件的存放路径`/tmp/ngx_cache/proxy_cache_dir`；
- **level path** 的目录层级 levels=1:2 表示两级目录；
- **keys_zone** 设置缓存名字和共享内存大小；
- **inactive** 在指定时间内没有被访问，缓存会被清理，默认10分钟。
- **max_size**最大缓存空间，如果缓存空间满，默认覆盖掉缓存时间最长的资源

使用proxy_cache，在server块配置文件中添加如下代码

```
proxy_cache mycache; # 指定上述的zone 或者off  默认off
proxy_cache_valid 200 304 1h; # 对于状态为200和304的缓存文件的缓存时间是1小时
proxy_cache_valid 301 302 1m;
proxy_cache_valid any 1m;
proxy_cache_key $host$request_uri;  # 定义缓存唯一key,通过唯一key来进行hash存取
proxy_next_upstream http_502 http_504 error timeout invalid_header; #出错尝试负载均衡中另外一个节点
add_header X-Cache-Status $upstream_cache_status; # 把缓存状态设置为头部信息，响应给客户端
proxy_no_cache $no_cache; # 判断该变量是否有值，如果有值则不进行缓存，如果没有值则进行缓存
proxy_cache_bypass $no_cache; #该指令用于配置Nginx服务器向客户端发送响应数据时，不从缓存中获取的条件，值判断方法同proxy_no_cache
proxy_cache_methods GET HEAD; #对GET HEAD方法进行缓存  默认 
proxy_hide_header   # 设置额外的响应头，这些响应头也不会发送给客户端
proxy_pass_header  # 与proxy_hide_header  相反
```

```
# $upstream_cache_status  变量状态码
MISS: 未命中缓存
HIT：命中缓存
EXPIRED: 缓存过期
STALE: 命中了陈旧缓存
REVALIDDATED: Nginx验证陈旧缓存依然有效
UPDATING: 内容陈旧，但正在更新
BYPASS: X响应从原始服务器获取
```

nginx默认会不缓存带cookie的页面，所以才导致nginx缓存都是MISS,  解决方法如下
```
proxy_ignore_headers X-Accel-Expires Expires Cache-Control Set-Cookie;
proxy_hide_header Set-Cookie;
```

对于一些实时性要求非常高或者注册等页面或数据来说，就不应该去设置缓存，下面来看看如何配置不缓存的内容，对于请求路径匹配/admin和/search 不缓存
```
 server {
 # URI 中后缀为 .txt 或 .text 的设置变量值为 "no cache"
    if ( $request_uri ~ ^/(admin|search)) {
      set $nocache "no-cache"; #非0为不缓存
     }
  ...
  localtion / {
      ...
        proxy_ignore_headers vary X-Accel-Expires Expires Cache-Control Set-Cookie;
        proxy_no_cache $nocache;
        proxy_cache_bypass $nocache;
        #proxy_hide_header      Set-Cookie;
        proxy_hide_header      Cache-Control;
        proxy_hide_header      server;
        proxy_hide_header      date;
        proxy_hide_header      vary;
    }
 
 }
```

#### server

 - listen 监听地址端口  默认`listen *:80 | *:8000 `
```
listen 127.0.0.1:8000;
listen 127.0.0.1; # 默认80端口
listen 8000;
listen *:8000;
listen localhost:8000;
listen [::]:8000;  # ipv6
listen [::1];
listen unix:/var/run/nginx.sock;
listen 443 ssl;  # https 
listen 8000 http2   # 端口配置为接受 HTTP/2 连接。
listen 80 default_server;  # 定义默认的server去处理一些没有匹配到 server_name 的请求
```

 - server_name 设置虚拟服务器的配置。  基于 IP（基于 IP 地址）和基于名称（基于“Host”请求标头字段）的虚拟服务器之间没有明确的区别

    Nginx 的虚拟主机是通 过HTTP请求中的Host值来找到对应的虚拟主机配置。如果找不到，那 Nginx 就会将请求送到指定了 default_server 的 节点来处理；如果没有指定为 default_server 的话,则会选取第一个定义的 server 作为 default_server
```
 server {
      listen 80 default_server;
      server_name _;
      ...
  }
server {
    server_name example.com *.example.com www.example.*;
    # server_name www.example.com ~^www\d+\.example\.com$;  # ~开头匹配正则
}
```

- 证书
```
  ssl_certificate devopshot.com_bundle.crt;   # 证书地址
  ssl_certificate_key devopshot.com.key;      # 私钥地址
  ssl_session_timeout 10m;
  ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # 支持ssl协议版本，默认为后三个，主流版本是[TLSv1.2]
   #请按照以下套件配置，配置加密套件，写法遵循 openssl 标准。
  ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE; 
  ssl_prefer_server_ciphers on;  # 指定在使用 SSLv3 和 TLS 协议时，服务器密码应优先于客户端密码  默认off
```

- 证书传输优化
客户端验证证书过程中，需要判断证书是否被被撤销失效等问题，需要再去访问 CA 下载 CRL 或者 OCSP 数据，这又会产生 DNS 查询、建立连接、收发数据等一系列网络通信，增加多个 RTT

OCSP stapling（Online Certificate Status Protocol stapling）是一种改进的证书状态确认方法，用于减轻证书吊销检查的负载，和提高数据传输的私密性。OCSP stapling将原本需要客户端实时发起的 OCSP 请求转嫁给服务端，服务端通过预先访问 CA 获取 OCSP 响应，然后在握手时随着证书一起发给客户端，免去了客户端连接 CA 服务器查询的时间

1、在 Nginx 中配置 OCSP stapling 服务
```
server {
    listen 443 ssl;
    server_name  www.mysite.cn;
    index index.html;

    ssl_certificate         server.pem;#证书的.cer文件路径
    ssl_certificate_key     server-key.pem;#证书的.key文件

    # 开启 OCSP Stapling 当客户端访问时 NginX 将去指定的证书中查找 OCSP 服务的地址，获得响应内容后通过证书链下发给客户端。
    ssl_stapling on;
    ssl_stapling_verify on;# 启用OCSP响应验证，OCSP信息响应适用的证书
    ssl_trusted_certificate /path/to/xxx.pem;# 若 ssl_certificate 指令指定了完整的证书链，则 ssl_trusted_certificate 可省略。
    resolver 8.8.8.8 valid=60s;#添加resolver解析OSCP响应服务器的主机名，valid表示缓存。
    resolver_timeout 2s；# resolver_timeout表示网络超时时间
```

2、检查服务端是否已开启 OCSP Stapling
```
openssl s_client -connect www.mysite.cn:443 -servername www.mysite.cn -status -tlsextdebug < /dev/null 2>&1 | grep "OCSP"
```

- 证书算法优化

SSL的证书根据算法不同可分为RSA证书和ECC证书，通常为了兼容性，大部分都使用 RSA 证书，不过在 Nginx 1.11.0 版本开始提供了对 RSA/ECC 双证书的支持。它的实现原理为分析在 TLS 握手中双方协商得到的 Cipher Suite，如果支持 ECDSA（基于ECC的签名算法）就返回 ECC 证书，否则返回 RSA 证书

ECC与RSA相比，拥有突出优势。
    - 更适用于移动互联网， ECC 加密算法的密钥长度很短，意味着占用更少的存储空间，更低的CPU开销和占用更少的带宽
    - 更好的安全性,ECC 加密算法提供更强的保护，比目前其他加密算法能更好地防止攻击.
    - 计算量小，处理速度更快，在私钥的处理速度上（解密和签名），ECC 远比 RSA、DSA 快得多。

密钥交换（ECDH）实现可以选择高性能的曲线实现，例如 x25519 或者 P-256。对称加密算法方面，也可以选用 AES_128_GCM 没有必要用更高长度的算法。

在 Nginx 里可以用 ssl_ciphers、ssl_ecdh_curve 等指令配置服务器使用的密码套件和椭圆曲线，把优先使用的放在前面，例如。

```
ssl_dyn_rec_enable on;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ecdh_curve X25519:P-256;
ssl_ciphers [ECDHE-ECDSA-CHACHA20-POLY1305|ECDHE-RSA-CHACHA20-POLY1305|ECDHE-ECDSA-AES256-GCM-SHA384|ECDHE-RSA-AES256-GCM-SHA384]:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:20m;
ssl_session_timeout 15m;
ssl_session_tickets off;
```
通过对 ECC、RSA、TLS1.2、TLS1.3 等不同维度的测试。

场景 | QPS Time   | 单次发出请求数
RSA证书 + TLS1.2  316.20  316.254ms   100
RSA证书 + TLS1.2 + QAT    530.48  188.507ms   100
RSA证书 + TLS1.3  303.01  330.017ms   100
RSA证书 + TLS1.3 + QAT    499.29  200.285ms   100
ECC证书 + TLS1.2  639.39  203.319ms   100
ECC证书 + TLS1.3  627.39  159.390ms   100

#### location

> `location` 根据请求 URI 设置配置

```
~* 正则表达式（用于不区分大小写的匹配）
~  正则表达式（用于区分大小写的匹配）
=  修饰符可以定义 URI 和位置的精确匹配。  如果找到完全匹配，则搜索终止。  例如，如果“/”请求频繁发生，定义“location = /”将加速这些请求的处理，因为搜索在第一次比较后立即终止。  这样的位置显然不能包含嵌套位置
^~ 匹配到即停止搜索；
@  前缀定义了一个命名位置。  这样的位置不用于常规请求处理，而是用于请求重定向
```

 - root 指定静态资源目录位置
```
# 例如：
location /i/ {
    root /data/w3;  # 当用户访问/i/top.gif时，实际在服务器找的路径是 /data/w3/i/top.gif
}
```

- alias 定义指定位置的替换
```
location /i/ {
    alias /data/w3/images/;  # alias 末尾一定要添加 /  如用户访问/i/top.gif时, 实际在服务器找的路径是 /data/w3/images/top.gif 
} 
# 注root 会将定义路径与 URI 叠加， alias 则只取定义路径， 当location匹配指令值的最后一部分时，最好用root
```

- index   将用作索引的默认文件
- return  停止处理请求，直接返回响应码或重定向到其他 URL ；执行 return 指令后， location 中后续指令将不会被执行。
```
# 值可以包含文本、变量及其组合
return 404; # 直接返回状态码
return 404 "pages not found"; # 返回状态码 + 一段文本
return 302 /bbs ; # 返回状态码 + 重定向地址
return http://xxx; # 返回重定向地址
```

- rewrite 根据指定正则表达式匹配规则，重写 URL 
```
# rewrite 正则表达式 要替换的内容 [flag] 可选的标志参数可以是
last 重写后的 URL 发起新请求，再次进入 server 段，重试 location 的中的匹配；
break 直接使用重写后的 URL ，不再匹配其它 location 中语句；
redirect 返回 302 临时重定向；
permanent 返回 301 永久重定向。
rewirte /images/(.*\.jpg)$ /pic/$1; # $1是前面括号(.*\.jpg)的反向引用
rewrite ^/users/(.*)$ /show?user=$1? last;
```

- if 表达式
```
# if (condition) { ... }
情况可以是以下任一情况
变量名称;如果变量的值为空字符串或“0”，则为 false;
= 或 != 相等或不等
使用“~”（用于区分大小写的匹配）和“~*”（对于不区分大小写的匹配）运算符将变量与正则表达式进行匹配。正则表达式可以包含可供以后在 $1..$9 变量中重用的捕获
-f 或 ！-f 运算符检查文件是否存在;
-d 或 ! -d 检测目录存在或不存在；
-e 或 ! -e 检测文件、目录、符号链接等存在或不存在；
-x 或 ! -x 检测文件可以执行或不可执行；
if ($http_cookie ~* "id=([^;]+)(?:;|$)") {
    set $id $1;
}
if ($request_method = POST) {
    return 405;
}
if ($invalid_referer) {
    return 403;
}
```

- autoindex  列出目录结构
```
autoindex on; # 打开 autoindex，，可选参数有 on | off
autoindex_exact_size on;
autoindex_format html;
autoindex_localtime off;  #是否显示时间 默认off
```

- expires  静态界面缓存时间 `expires 1M`
- try_files 类似rewrite的指令，提高解析效率 `try_files $uri $uri/ /images/default.gif`
- allow 192.168.1.0/32;  # 允许访问指定的网络或地址
- deny  all;   # 拒绝对指定网络或地址的访问
- limit_except 限制location内允许的 HTTP 方法,限制位置内允许的 HTTP 方法
```
# 方法参数可以是以下之一：GET、HEAD、POST、PUT、DELETE、MKCOL、COPY、MOVE、OPTIONS、PROPFIND、PROPPATCH、LOCK、UNLOCK 或 PATCH
limit_except GET {
    allow 192.168.1.0/32; 
    deny  all;  
}
```

- satisfy  控制多个模块之间彼此协作  默认all，也就是“与”关系，另一种为 any 方式，也就是“或”关系
```
# 通过192.168.1.0段的ip直接访问，其他需要验证
location / {
    satisfy any;
    allow 192.168.1.0/24;
    deny  all;
    auth_basic           "closed site";
    auth_basic_user_file conf/htpasswd;
}
```


#### 负载均衡
 1. 轮询策略：默认情况下采用的策略，将所有客户端请求轮询分配给服务端。这种策略是可以正常工作的，但是如果其中某一台服务器压力太大，出现延迟，会影响所有分配在这台服务器下的用户；
 2. 最小连接数策略：将请求优先分配给压力较小的服务器，它可以平衡每个队列的长度，并避免向压力大的服务器添加更多的请求；
 3.  最快响应时间策略：优先分配给响应时间最短的服务器；
 4. 客户端 IP 绑定策略：来自同一个 IP 的请求永远只分配一台服务器，有效解决了动态网页存在的 session 共享问题。


- upstream  定义一组服务器（指的就是后台应用服务器）的相关信息
```
# 语法 upstream name { ... }  上下文 http
upstream dynamic {
    zone upstream_dynamic 64k;
    server backend1.example.com      weight=5;
    server backend2.example.com:8080 fail_timeout=5s slow_start=30s;
    server 192.0.2.1                 max_fails=3;
    server backend3.example.com      resolve;
    server backend4.example.com      service=http resolve;
    server backup1.example.com:8080  backup;
    server backup2.example.com:8080  backup;
    keepalive 8;
}
server {
    location / {
        proxy_pass http://dynamic;
    }
} 
```
在 upstream 常用指令：
     - server 定义后端服务器地址；
     - zone 定义共享内存区域的名称和大小，用于跨 worker 子进程 
     - keepalive 对上游服务启用长连接，    设置到每个工作进程缓存中保留的上游服务器的最大空闲保持活动连接数
     - keepalive_requests 一个长连接最多请求 HTTP 的个数；1.19.10版本默认1000
     - keepalive_time  限制可以通过一个保持活动连接处理请求的最长时间 默认1h
     - keepalive_timeout  空闲情形下，一个长连接的超时时长
     - hash 哈希负载均衡算法；
```
# 通过制定关键字作为 hash key ，基于 hash 算法映射到特定的上游服务器中。关键字可以包含有变量、字符串。
upstream demo_server {
  hash $request_uri;
  server backend1.example.com;
  server backend2.example.com;
}
hash $request_uri 表示使用 request_uri 变量作为 hash 的 key 值，只要访问的 URI 保持不变，就会一直分发给同一台服务器
```

     - ip_hash 客户端 IPv4 地址的前三个八位字节或整个 IPv6 地址进行哈希计算的负载均衡算法； 
```
根据客户端的请求 IP 进行判断，只要 IP 地址不变就永远分配到同一台主机。它可以有效解决后台服务器 session 保持的问题
upstream demo_server {
  ip_hash;
  server backend1.example.com;
  server backend2.example.com;
}
```

     - least_conn 最少连接数负载均衡算法，同时考虑服务器的权重；
```
upstream demo_server {
  zone test 1M; # zone可以设置共享内存空间的名字和大小
  least_conn;
  server backend1.example.com;
  server backend2.example.com;
}
```

     - least_time 最短响应时间负载均衡算法，同时考虑服务器的权重；
     - random 随机负载均衡算法，同时考虑服务器的权重;
     - ntlm 允许使用 NTLM 身份验证代理请求
```
# 为了使 NTLM 身份验证正常工作，必须启用与上游服务器的保持连接。proxy_http_version指令应设置为“1.1”，并应清除“连接”标头字段
upstream http_backend {
    server 127.0.0.1:8080;
    ntlm;
}
server {
    ...
    location /http/ {
        proxy_pass http://http_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        ...
    }
}
```

     - server 定义上游服务器地址
```
# server address [parameters];
    parameters 可选值：
      weight=number 权重值，默认为1；
      max_conns=number 上游服务器的最大并发连接数 默认为0 没有限制；
      fail_timeout=time 服务器不可用的判定时间 默认10s；
      max_fails=numer 服务器不可用的检查次数 默认1；
      backup 备份服务器，仅当其他服务器都不可用时才会启用；
      down 标记服务器长期不可用，离线维护。
      resolve 监控与服务器域名对应的IP地址的变化，并自动修改上游配置， 为了使此参数正常工作，必须在 http 块或相应的上游块中指定resolver指令
      route 设置服务路由名称
      slow_start 慢启动， 默认0表示禁用， 当服务器从不可用状态恢复过来时，通过slow_start设置的值决定将服务器权重从0逐渐恢复到正常设置值的时间。（在哈希、IP哈希、随机三种负载均衡模式下不可用）
      drain 将服务器设置为“draining"模式，这种模式下，只有绑定到服务器的请求才会被代理到该服务器上
```

     - sticky 会话一致性，这将来自同一客户端的请求传递到一组服务器中的同一服务器
```
# 目前支持三种模式的会话一致性
# 1.cookie，来自尚未绑定到特定服务器的客户端的请求将传递到由配置的平衡方法选择的服务器。使用此 Cookie 的进一步请求将传递到指定的服务器。如果指定的服务器无法处理请求，则选择新服务器，就好像客户端尚未绑定一样
# Cookie 值是 IP 地址和端口的 MD5 哈希值或 UNIX 域套接字路径的十六进制表示形式。但是，如果指定了服务器指令的“route”参数，则 cookie 值将是 “route” 参数的值
upstream backend {
    server backend1.example.com;
    server backend2.example.com;
    sticky cookie srv_id expires=1h domain=.example.com path=/;
}
upstream backend {
    server backend1.example.com route=a;
    server backend2.example.com route=b;
    sticky cookie srv_id expires=1h domain=.example.com path=/;
}
在这种情况下，“srv_id”cookie 的值将为 a 或 b。
# 2. Sticky Routes也是在backend第一次response之后，会产生一个route信息，route信息通常会从cookie/URI信息中提取。
sticky route $route_cookie $route_uri;
这样Nginx会按照顺序搜索routecookie、route_uri参数并选择第一个非空的参数用作route，而如果所有的参数都是空的，就使用上面默认的负载均衡算法决定请求分发给哪个backend。
# 3. learn较为的复杂也较为的智能 nginx会分析上游服务器响应，Nginx会自动监测request和response中的session信息，而且通常需要回话一致性的请求、
应答中都会带有session信息，这和第一种方式相比是不用增加cookie，而是动态学习已有的session
这种方式需要使用到zone结构，在Nginx中zone都是共享内存，可以在多个worker process中共享数据用的
一个兆字节区域可以在 64 位平台上存储大约 4000 个会话。在超时参数指定的时间内未访问的会话将从区域中删除。默认情况下，超时设置为 10 分钟。
upstream backend {
   server backend1.example.com:8080;
   server backend2.example.com:8081;
   sticky learn
       create=$upstream_cookie_examplecookie
       lookup=$cookie_examplecookie
       zone=client_sessions:1m;
}
```



#### 压测

```
siege -c 100 -t 200S -v xx
ab -c 50 -n 100  xx
```