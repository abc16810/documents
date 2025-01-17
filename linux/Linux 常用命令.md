查看某个进程下的线程

```
ps -T -p <pid>  # -T选项可以开启线程查看。下面的命令列出了由进程号为<pid>的进程创建的所有线程
top -H -p <pid>  # -H top命令可以实时显示各个线程情况
```

查看进程GC

```
jstat -gcutil pid 1000 1000   # 1000ms统计一次gc情况统计1000次
```

IP地址

```shell
# grep -Eo  E扩展正则，o 只打印匹配行中匹配的(非空的)部分
ip addr show | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'
```

网络连接数目

```
# cut -c 68- 从第68个字符截取到末尾
netstat -an | grep -E “^(tcp)” | cut -c 68- | sort | uniq -c | sort -n
netstat -n | awk '/^tcp/ {++b[$NF]} END {for(a in b) print a,"\t",b[a]}'
# 远程IP连接数
netstat -antu| awk '$5~/^[0-9]/ { split($5,a,":");ips[a[1]]++} END {for (i in ips) print ips[i] ,i}'
```

查看最常用的命令和使用次数

```
history |awk ' {if($2 == "sudo") a[$3]++ ;else a[$2]++} END {for(i in a){print a[i] " " i} }' |sort -rn |head 
```

查看swap使用情况

```
# cat /proc/pid/smaps |grep Swap
for i in $(ls /proc | grep "^[0-9]" | awk '$0>100'); do awk '/Swap:/{a=a+$2}END{print '"$i"',a/1024}' /proc/$i/smaps;done| sort -k2nr |awk '$2>0 {print  $1,  $NF"M"}'
```

统计私有ip地址

```
# 10.x.x.x 172.x.x.x  192.168.x.x
ip addr | \
       awk -F '[ /]+' 'BEGIN{
            PRIVATE_PREFIX["10"]="";
            PRIVATE_PREFIX["172"]="";
    }
    /inet /{
            split($3, A, ".");
            if (A[1] in PRIVATE_PREFIX) {
                    print $3
            }

            if ((A[1] == 192) && (A[2] >= 168)) {
                    print $3
            }
    }'
```

删除cpu大于40的进程

```
#!/bin/sh
ps aux | grep -vw sshd64 | awk '{if($3>40.0) print $2}' | while read procid
do
kill -9 $procid
done
```



