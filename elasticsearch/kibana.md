kibana 连接ES  版本为（1.17.1）

#### es启用https 如下配置

**PEM**类型证书

```
- node.name=es01
...
- xpack.security.http.ssl.enabled=true
- xpack.security.http.ssl.key=$CERTS_DIR/es01/es01.key
- xpack.security.http.ssl.certificate=$CERTS_DIR/es01/es01.crt
- xpack.security.http.ssl.key_passphrase=111222
- xpack.security.http.ssl.certificate_authorities=$CERTS_DIR/ca.crt
# openssl pkcs12 -in http.p12 -out ca.crt  -clcerts -nokeys 可以导出客户端证书
```

kibana 配置

```
elasticsearch.hosts: ["https://es01:9200"]
elasticsearch.ssl.certificateAuthorities: ["/usr/share/kibana/ca.crt"] # 即为es中的ca.crt
```

**PKCS#12**类型的证书

```
# es 配置
- xpack.security.http.ssl.enabled=true
- xpack.security.http.ssl.keystore.path=$CERTS_DIR/http.p12
# - xpack.security.http.ssl.truststore.path=$CERTS_DIR/http.p12
# 如下是明文指定密码 或者用ssl.truststore.secure_password 加密指定
# - xpack.security.http.ssl.truststore.password=123456 
- xpack.security.http.ssl.client_authentication=required

# kibana
#kibana访问es集群 
elasticsearch.ssl.verificationMode: certificate # 跳过主机名验证  默认 full 验证主机名
elasticsearch.ssl.keystore.path: "/usr/share/kibana/http.p12"
elasticsearch.ssl.keystore.password: "123456" # 明文指定密码
```



#### es启用认证（需要输入用户名和密码） kibana配置如下

```
elasticsearch.username: "elastic"
elasticsearch.password: "123456
```



#### kibana启用SSL

```text
# 来自 Kibana 服务器的传出请求的 SSL（PEM 格式）
server.ssl.enabled: true
server.ssl.key: /path/to/your/server.key
server.ssl.certificate: /path/to/your/server.crt
```



