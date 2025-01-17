#### 拉取镜像

```
docker pull prom/prometheus
```

#### docker-compose.yml

```

version: '3.7'

services:
  alertmanager:
    image: prom/alertmanager:latest
    volumes:
      - type: bind
        source: /home/prom/alertmanager/alertmanager.yml
        target: /etc/alertmanager/alertmanager.yml
        read_only: true
    ports:
      - "9093:9093"
      - "9094:9094"
    networks:
      - prom

  prometheus:
    depends_on:
      - alertmanager
    image: prom/prometheus:latest
    volumes:
      - type: bind
        source: /home/prom/prometheus/prometheus.yml
        target: /etc/prometheus/prometheus.yml
        read_only: true
      - type: bind
        source: /home/prom/prometheus/alert-rules.yml
        target: /etc/prometheus/alert-rules.yml
        read_only: true
      - type: volume
        source: prometheus
        target: /prometheus
    ports:
      - "9090:9090"
    networks:
      - prom

  grafana:
    depends_on:
      - prometheus
    image: grafana/grafana:latest
    volumes:
      - type: volume
        source: grafana
        target: /var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - prom

# docker volume create --driver local  --opt type=none --opt o=bind --opt device=/home/prom/prometheus/data
# 数据即在/x/data目录一下一份，还在相应的volume下存放一份
volumes:
  prometheus:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/prom/prometheus/data
  grafana:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/prom/grafana
      
networks:
  prom:
    driver: bridge
```



#### 相关配置

**prometheus.yml**

```
global:
  scrape_interval:     15s   # 采集（拉取）监控目标信息间隔  默认1m
  evaluation_interval: 15s   # 触发告警检测的时间 默认1m

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093   # 告警管理服务

rule_files:
  - "*rules.yml"     # 规则文件

scrape_configs:            # 监控目标配置
  - job_name: 'prometheus'
    static_configs:
    - targets: ['prometheus:9090']

  - job_name: '10.4.55.209'
    static_configs:
    - targets: ['10.4.55.209:9100']
      labels:
       nodes: Prometheus

  - job_name: 'alertmanager'
    static_configs:
    - targets: ['alertmanager:9093']
```



**alertmanager.yml**

```
global:
  resolve_timeout: 5m
route:
  group_by: ['cqh'] # 警报分组
  group_wait: 10s #组报警等待时间
  group_interval: 10s #组报警间隔时间
  repeat_interval: 1m #重复报警间隔时间
  receiver: 'web.hook'
receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://10.211.55.2:8888/open/test'
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
```



https://prometheus.io/docs/prometheus/latest/installation/

