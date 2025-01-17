#### amtool 工具

amtool是一个cli工具，用于与Alertmanager API交互。它与Alertmanager的所有版本捆绑在一起。



查看所有当前发出的警报

```
# amtool alert
docker  exec -it c77b083377d3  amtool --alertmanager.url=http://localhost:9093  alert

Alertname          Starts At                Summary                                       
NodeDiskOtherHigh  2022-03-30 15:07:36 UTC  instance: 10.4.56.207:9100 disk( /srv) 使用率过高  
NodeMemoryHigh     2022-04-06 02:26:21 UTC  instance: 10.4.56.209:9100 memory 使用率过高

# 使用扩展输出查看所有当前触发的警报
amtool -o extended alert

# 除了查看警报之外，还可以使用Alertmanager提供的富查询语法
amtool -o extended alert query alertname="NodeMemoryHigh"
amtool -o extended alert query job=~".+mysql"
amtool -o extended alert query alertname=~"Test.*" instance=~".+1"
```

静默一个警告

```
# 添加静默
amtool silence add alertname=NodeMemoryHigh  --comment='test'
# 查询静默
amtool silence query
amtool silence query instance=~".+0"
# 静默过期
amtool silence expire 6b3d5f61-3d36-4750-8194-763cddb26242
amtool silence expire $(amtool silence query -q instance=~".+0")
amtool silence query instance=~".+0"
# 所有沉默过期
amtool silence expire $(amtool silence query -q)
```

配置

为了方便，Amtool允许配置文件指定一些选项。默认配置文件路径为`$HOME/.config/amtool/config.yml`或`/etc/amtool/config.yml`

```
# Define the path that `amtool` can find your `alertmanager` instance
alertmanager.url: "http://localhost:9093"

# Override the default author. (unset defaults to your username)
author: me@example.com

# Force amtool to give you an error if you don't include a comment on a silence
comment_required: true

# Set a default output format. (unset defaults to simple)
output: extended

# Set a default receiver
receiver: default
```

