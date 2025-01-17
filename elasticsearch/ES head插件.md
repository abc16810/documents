

elasticsearch-head是基于nodejs开发的，所以需要安装nodejs环境

```
# node --version
v14.3.0
```

下载elasticsearch-head

```
git clone git://github.com/mobz/elasticsearch-head.git
cd elasticsearch-head
npm install  # 改命令安装会报错
npm install phantomjs-prebuilt@2.1.16 --ignore-scripts   # 忽略输出警告
```

修改Gruntfile.js文件

```
                connect: {
                        server: {
                                options: {
                                        hostname: "0.0.0.0",   # 增加
                                        port: 9100,
                                        base: '.',
                                        keepalive: true
                                }
                        }
                }
```

编辑`_site/app.js`找到this.base_uri这里，把localhost改为本机ip

```
this.base_uri = this.config.base_uri || this.prefs.get("app-base_uri") || "http://本机ip:9200";
```

启动

```
npm run start
```



当ES启用https 和基本验证时

```
http://head_ip:9100/?auth_user=elastic&auth_password=xx&base_uri=https://es:9200/
```



​	