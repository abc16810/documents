#### docker安装

```
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.5.2
# 单节点测试，Docker启动单个节点集群
# docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.5.2
```

- 设置 `vm.max_map_count`

对于生产环境，必须将 `vm.max_map_count`内核设置设置为至少262144

```
grep vm.max_map_count /etc/sysctl.conf
vm.max_map_count=262144
# sysctl -w vm.max_map_count=262144
```

- 配置ulimit  将`nofile和nproc` 配置为65535或更高

Elasticsearch容器必须增加nofile和nproc的ulimit。验证Docker守护进程的init系统，将它们设置为可接受的值

```
# /etc/security/limits.conf
elasticsearch  -  nofile  65535

# docker run --rm centos:7 /bin/bash -c 'ulimit -Hn && ulimit -Sn && ulimit -Hu && ulimit -Su'
1048576
1048576
unlimited
unlimited
```

- 禁用swapping

为了提高性能和节点稳定性，需要关闭交换机交换功能

```
-e "bootstrap.memory_lock=true" --ulimit memlock=-1:-1
```

- 设置heap size

使用ES_JAVA_OPTS环境变量设置堆大小

```
-e ES_JAVA_OPTS="-Xms16g -Xmx16g"
```

- 配置数据目录权限

默认情况下，Elasticsearch使用uid:gid 1000:1000作为用户Elasticsearch在容器中运行，elasticsearch用户必须能够读取挂载的本地目录或文件，一个好的策略是为改挂载的本地目录的设置组访问（gid ）为1000或0。

```
mkdir esdatadir
chmod g+rwx esdatadir
chgrp 1000 esdatadir
```

或者指定变量` -e TAKE_FILE_OWNERSHIP=true`

#### docker-compose.yml配置

```
version: '3'

services:
  es01:
    image: elasticsearch:7.17.1
    container_name: es01
    environment:
      - node.name=es01
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=es02,es03
      - cluster.initial_master_nodes=es01,es02,es03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - "ES_LOG_STYLE=file"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - ./conf/es01.yml:/usr/share/elasticsearch/config/elasticsearch.yml
      - data01:/usr/share/elasticsearch/data
    ports:
      - 9200:9200
    networks:
      - elastic
  es02:
    image: elasticsearch:7.17.1
    container_name: es02
    environment:
      - node.name=es02
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=es01,es03
      - cluster.initial_master_nodes=es01,es02,es03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - data02:/usr/share/elasticsearch/data
    networks:
      - elastic
  es03:
    image: elasticsearch:7.17.1
    container_name: es03
    environment:
      - node.name=es03
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=es01,es02
      - cluster.initial_master_nodes=es01,es02,es03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - data03:/usr/share/elasticsearch/data
    networks:
      - elastic

volumes:
  data01:
    driver: local
  data02:
    driver: local
  data03:
    driver: local

networks:
  elastic:
    driver: bridge
```

通过命令`docker-compose up -d` 启动集群, 访问http://ip:9200/

```
curl http://localhost:9200/?pretty  #  查看集群工作正常与否的信息
# 查看群集节点
curl -X GET http://localhost:9200/_cat/nodes
192.168.192.2 33 92 0 0.03 0.06 0.05 cdfhilmrstw * es01
192.168.192.3 57 92 0 0.03 0.06 0.05 cdfhilmrstw - es02
192.168.192.4 18 92 0 0.03 0.06 0.05 cdfhilmrstw - es03
# 健康状况
curl  -X GET http://localhost:9200/_cat/health  # _cat/health?v 详细信息
1648717837 09:10:37 es-docker-cluster green 3 3 6 3 0 0 0 0 - 100.0%
# green：所有的主分片和副本分片都正常运行。
# yellow：所有的主分片都正常运行，但不是所有的副本分片都正常运行。
# red：有主分片没能正常运行。
# 查看是否锁定内存
curl http://localhost:9200/_nodes?filter_path=**.mlockall
# 查看文件描述符设置
curl http://localhost:9200/_nodes/stats/process?filter_path=**.max_file_descriptors
# list所有索引
curl  -X GET http://localhost:9200/_cat/indices?v
```

#### 注意事项

1、始终绑定数据卷。您应该使用卷绑定到`/usr/share/elasticsearch/data`，原因如下

- 防止数据丢失，即使容器被杀死，Elasticsearch节点的数据也不会丢失
- 快速的IO，Elasticsearch是I/O敏感的，Docker存储驱动程序对于快速I/O并不理想
- 它允许使用高级Docker卷插件

2、避免使用loop-lvm模式。如果您正在使用devicemapper存储驱动程序，请不要使用默认的loop-lvm模式。配置docker-engine使用direct-lvm 

3、日志收集。考虑使用不同的日志驱动程序来集中日志。还要注意，默认的json文件日志驱动程序并不适合于生产使用， docker下默认输出到console  可以指定变量`ES_LOG_STYLE`  为file 将按照`log4j2.properties` 存储日志

4、挂载自定义配置文件。当你在Docker中运行时，Elasticsearch的配置文件会从`/usr/share/ Elasticsearch /config/`中加载。要使用自定义配置文件，需要将这些文件绑定到映像中的配置文件上。也可以使用Docker环境变量设置单独的Elasticsearch配置参数

[官网](https://www.elastic.co/guide/en/elasticsearch/reference/7.5/docker.html)

[docker](https://github.com/elastic/elasticsearch/blob/7.5/distribution/docker/docker-compose.yml)