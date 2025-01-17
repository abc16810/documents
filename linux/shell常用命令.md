#### grep
> 常用的grep选项有

 - -c  之输出匹配行的计数
 - -i 不区分大小写（只适用于单字符）
 - -h 查询多文件时不显示文件名
 - -l 查询多文件时只输出包含匹配字符的文件名
 - -n 显示匹配行及行号
 - -s 不显示不存在或者无匹配文本的错误信息
 - -v 显示不包含匹配文本的所有行
 
```
$ grep "sort" *.doc   # 当前目录下所有 .doc文件中查找字符串“sort”
$ grep -c "48" data # 返回数字4，意义是有 4行包含字符串"66"
 
$ grep -n 'root' /etc/passwd  # 显示满足匹配模式的所有行行数
1:root:x:0:0:root:/root:/bin/bash
37:nm-openvpn:x:118:124:NetworkManager OpenVPN,,,:/var/lib/openvpn/chroot:/usr/sbin/nologin

```
精确匹配 

使用grep抽取精确匹配的一种更有效方式是在抽取字符串前后加 `\>` 。假定现在精确匹配`root`
```
$ grep -n '\<root\>' /etc/passwd
1:root:x:0:0:root:/root:/bin/bash

```
grep和正则表达式

使用正则表达式使模式匹配加入一些规则，因此可以在抽取信息中加入更多选择。使用
正则表达式时最好用单引号括起来
```
grep '^[^0-9]' /etc/passwd   # 匹配非数字开头的所有行

grep 's\{2,\}'  /etc/passwd  # 字符s至少重复出现两次的所有行
```
grep 命令加 -E参数，这一扩展允许使用扩展模式匹配
```
grep -E '2|A'  /etc/passwd   # 打印包含2或A的行
```

egrep代表expression或extended grep ，适情况而定。 egrep接受所有的正则表达式， egrep的一个显著特性是可以以一个文件作为保存的字符串，然后将之传给 egrep作为参数匹配，为此使用-f开关。



#### find

 - -name  按照文件名查找文件。
 - -perm  按照文件权限来查找文件。
 - -prune  使用这一选项可以使 find命令不在当前指定的目录中查找，如果同时使用了 - depth选项，那么 -prune选项将被find命令忽略。
 - -user  按照文件属主来查找文件。
 - -group  按照文件所属的组来查找文件。
 - -mtime -n +n  按照文件的更改时间来查找文件， -n表示文件更改时间距现在n天以内，+n表示文件更改时间距现在n天以前。find命令还有- atime 和-ctime选项，但它们都和 -mtime选项相似，所以我们在这里只介绍 -mtime选项。
 - -nogroup  查找无有效所属组的文件，即该文件所属的组在/etc/groups中不存在。
 - -nouser  查找无有效属主的文件，即该文件的属主在 /etc/passwd中不存在。
 - -newer file1 ! file2  查找更改时间比文件file1新但比文件file2旧的文件。
 - -type  查找某一类型的文件，诸如：b块设备文件。d目录。c 字符设备文件。p管道文件。l 符号链接文件。f 普通文件。
 - -size n[c]  查找文件长度为n块的文件，带有c时表示文件长度以字节计。
 - -depth  在查找文件时，首先查找当前目录中的文件，然后再在其子目录中查找。
 - -fstype  查找位于某一类型文件系统中的文件，这些文件系统类型通常可以在配置文件/etc/fstab中找到，该配置文件中包含了本系统中有关文件系统的信息。
 - -mount  在查找文件时不跨越文件系统mount点。
 - -follow  如果find命令遇到符号链接文件，就跟踪至链接所指向的文件。
 - -cpio  对匹配的文件使用cpio命令，将这些文件备份到磁带设备中。

```
# 在当前目录及子目录中查找所有的.txt后缀文件
$ find . -name "*.txt" -print
# 当前目录及子目录中查找文件名以一个大写字母开头的文件
$ find . -name "[A-Z]*" -print
# 在/etc目录中查找文件名以host开头的文件
$ find /etc -name "host*" -print
# 在当前目录查找文件名以两个小写字母开头，跟着是两个数字，最后是 *.txt的文
件，下面的命令就能够返回名为aa22.txt的文件
$ find /tmp  -name "[a-z][a-z][0-9][0-9].txt" -print
# 当前目录下查找权限位为755的文件和目录
$ find . -perm 755 -print 
# 当前目录下查找所有用户都可读、写、执行的文件
$ find . -perm -007 -print
# 当前目录下查找更改时间在 5日以内的文件
$ find . -mtime -5 -print
# 在/var/log目录下查找更改时间在 3日以前的文件
$ find /var/log -mtime +3 -print
# 在 /etc目录下查找所有的目录
find /etc -type d -print
# 在当前目录下查找除目录以外的所有类型的文件
find . ! -type d -print 
# 在当前目录下查找文件长度大于1M字节的文件
$ find . -size +1000000c -print
# 在当前目录下查找长度超过10块的文件（一块等于 5 1 2字节）
$ find . -size +10 -print 
# 在当前目录下查找文件大小大于10M的文件
$ find . -size +10M -print

# 匹配到了当前目录下的所有普通文件，并在-exec选项中使用ls -l命令将它们列出。
$ find . -type f -exec ls -l {} \;
# 在/var/log目录中查找更改时间在5日以前的文件并删除它们
$  find /var/log/ -type f -mtime +5 -exec rm  {} \;  

# 交互模式 在/var/log目录中查找更改时间在 5日以前的文件并删除它们 按y键删除文件，按n键不删除。
$  find /var/log/ -type f -mtime +5 -ok rm  {} \; 
< rm ... /var/log/fontconfig.log > ? y
rm: 无法删除 '/var/log/fontconfig.log': 权限不够
< rm ... /var/log/lastlog > ? n

# print0 让 find命令在打印出一个文件名之后接着输出一个 NUL字符 ('') 而不是换行符
$ find /home   -size +1M  -print0 

# xargs -0 用NUL字符来作为记录的分隔符 。这样组合可以删除有空格的文件
$ sudo find . -type f -name "*.txt"  -print0 |xargs -0  rm 
```


#### xargs


之所以能用到这个命令，关键是由于很多命令不支持|管道来传递参数，而日常工作中有有这个必要，所以就有了xargs命令，例如：
```
find /var/log  -type f |ls -l      这个命令是错误的
find /var/log  -type f |xargs ls -l   这样才是正确的
```

> -n num 后面加次数，表示命令在执行的时候一次用的argument的个数，默认是用所有的。

```
$ ls |xargs -n 1 echo
11.txt
22.txt
$ ls |xargs -n 2 echo
11.txt 22.txt
$ ls |xargs  echo
11.txt 22.txt

```
> -t 表示先打印命令，然后再执行

```
$ ls |xargs -t echo 
echo 11.txt 22.txt 
11.txt 22.txt
```
> -i 或者是-I，这得看linux支持了，将xargs的每项名称，一般是一行一行赋值给{}，可以用{}代替

```
$ ls |xargs -t -i mv {} {}.back
mv 11.txt 11.txt.back 
mv 22.txt 22.txt.back 
$ find .  -name   "*.py" |xargs -t -i sed -i '/#!/a\#-*-coding:utf-8-*-' {}
```

在使用**find**命令的`-exec`选项处理匹配到的文件时， **find**命令将所有匹配到的文件一起传递给`exec`执行。不幸的是，有些系统对能够传递给`exec`的命令长度有限制，这样在 **find**命令运行几分钟之后，就会出现溢出错误。错误信息通常是“参数列太长”或“参数列溢出” 。这就是x**xargs**命令的用处所在，特别是与**find**命令一起使用。 **find**命令把匹配到的文件传递给**xargs**命令，而**xargs**命令每次只获取一部分文件而不是全部，不像`-exec`选项那样。这样它可以先处理最先获取的一部分文件，然后是下一批，并如此继续下去。在有些系统中，使用`-exec`命令时，究竟是一次获取所有的参数，还是分批取得参数，以及每一次获取参数的数目都会根据该命令的选项及系统内核中相应的可调参数来确定


#### sed
sed是一个强大的文本过滤工具。使用sed可以从文件或字符串中抽取所需信息

- N：将数据流中下下一行加进来创建一个多行组来处理
- D：删除多行组中的一行
- P：打印多行组中的一行
- n 单行next命令小写的n命令会告诉sed编辑器匹配移动到数据流中的下一文本行，而不用重新回到命令的最开始再执行一遍
  
```
$ cat test 
11

22

33
$ sed '/11/{n;d}' test
11
22

33
```

大写N会将下一行文本加到已经再模式空间中的文本上，这样的作用是将数据流中的两个文本行合并到同一个模式空间。文本行仍然用换行符分隔，但sed编辑器现在会将两行文本当成一行来处理
```
$ sed '/first/{N; s/\n/ /}' test
first second
last
```
如果短语被分隔成两行，用N，但是如果匹配的数据在最后一行，命令就不会发现要匹配的数据
```
$ sed 'N; s/first\nsecond/2222/' test
2222
last

$ sed 'N; s/last/2222/' test
first
second 22
last    # 没有匹配
```

通配符(.)来匹配空格和换行符，但当它匹配换行符时，它就从字符串中删掉了换行符，导致两行合并成一行

小写d删除模式空间中的当前行，但和N命令一起使用时，模式空间中的两行都被删除
```
$ sed 'N; /first/d' test    # 删除匹配行和上下一行， 如果是最后一行，则删除最后2行
```

多行删除命名D 它只删除模式空间中的第一行，它会删除到换行符（含换行符）的所有字符
```
$ sed 'N; /11\n22/D' test2    # 删除的第一行11 ，第二行没有删除
22
33
```

当多行匹配出现时，P命令只会打印模式空间中的第一行
```
$ sed -n 'N; /11\n22/P' test2
11
```

**保持空间**

 - h: 将模式空间复制到保持空间
 - H：将模式空间附加到保持空间
 - g:  将保持空间复制到模式空间
 - G：将保持空间附加到模式空间
 - x：交换模式空间和保持空间的内容

```
$ cat test
this is a header line
this is a first line
this is a second line
this is a last line

$ sed -n '/first/{
> h
> p
> n
> p
> g
> p
> }' test
this is a first line
this is a second line
this is a first line

```

1. sed脚本在地址中用正则表达式来过滤出含first的行
2. 当含first行出现时，h命令将改行放到保持空间
3. p命令打印模式空间，也就是第一个数据行的内容
4. n命令提取数据流中的下一行,并将它放到模式空间
5. p命令打印模式空间的内容
6. g命令将保持空间的内容放回模式空间，替换当前文本
7. p命令打印模式空间的当前内容


`!` 排除命令

```
$ sed -n '/head/!p' test
this is a first line
this is a second line
this is a last line

# 最后一行，不执行N命令，但它对其它行都执行这个命令。 $表示数据流中最后一行文本
$ sed '$!N; s/last.line/three line/' test
this is a header line
this is a first line
this is a second line
this is a three line

# 反转文本内容
$ sed -n '{1!G; h; $p}' test
this is a last line
this is a second line
this is a first line
this is a header line

sed '$!G' /tmp/passwd  #加倍行间距 $! 排除最后一行保持空间 即最后一行不添加空行
sed '/^$/d;$!G' /tmp/22  #先删除所有空白行，在加倍行间距
# sed = 号显示数据流中的行的行号
$ sed '=' test
```

**跳转** [address]b [label]

```
# 跳过1-3行匹配替换
$ sed '{1,3b; s/this is/Is this/; s/a/A?/}' test
this is a header line
this is a first line
this is a second line
Is this A? last line

# 如果指定标签，将它加到b命令后面 如jump1  这样允许你在匹配的跳转地址跳过一些命令，但仍然执行脚本中的其它命令
$ sed '{/first/b jump1; s/this is a/No jump on/;  :jump1 s/this is a/Jump here on/}' test
No jump on header line
Jump here on first line
No jump on second line
No jump on last line

# 也可以跳到脚本中前面的标签上， 行中有逗号的情况下跳转，直到最后一个逗号
$ echo "This, is, a, test, to, remove, commas. " |sed -n '{:start s/,//1p; /,/b start}'
This is, a, test, to, remove, commas. 
This is a, test, to, remove, commas. 
This is a test, to, remove, commas. 
This is a test to, remove, commas. 
This is a test to remove, commas. 
This is a test to remove commas. 

# 测试t  类似b跳转命令
$ sed '{ s/first/matched/; t; s/this is a/no match on/}' test
no match on header line
this is a matched line
no match on second line
no match on last line

# 如果匹配的行中的模式，它会替换文本，而且测试命令会跳过后面的命令
$ echo "this, is, a, test, to, remove, commas."|sed -n '{:start s/,//1p; t start}'
```






#### awk



**操作符**

匹配正则表达式，使用符号‘～’后紧跟正则表达式，也可以用 i f语句。 awk中if 后面的条件用（）括起来

`\ ^ $ . [] | () * + ?` 

 - `+` 使用+匹配一个或多个字符。
 - `?` 匹配模式出现频率0次或1次。例如使用 /XY?Z/ 匹配XYZ或XZ。
 - `<, <=, ==, !=, >=`  关系操作符
 - `~ !~`   匹配，不匹配
 - `|| && !`  并与非 
 - `= += *= /= %= ^=`  赋值操作符


```
# 指定的分割符第5列匹配root的打印
$ awk -F ':' '{if($5~/root/) print $0}'  /etc/passwd
root:x:0:0:root:/root:/bin/bash
$ awk '$0~/root/'  /etc/passwd  # 记录包含模式root，就打印它
# 不匹配（~） 表达式 $0!~/root/ ，意即查询不包含模式root字符的记录并打印它
$ awk '{if($6<$7) print $0}' test.txt  # 小于匹配
$ awk '{if($6<=$7) print $0}' test.txt  # 小于等于
$ awk '$4~/[Gg]reen/ ' test.txt   # 不区分大小写匹配green
$ awk '$1~/^...a/ ' test.txt   # 前3个任意字符及第4个字符为a的匹配
# 重新赋值学生名域为 name，级别域为 belts。查询级别为 Yellow的记录，并最终打印名称和级别
$ awk '{name=$1;belts=$4; if(belts~/yellow/) print name " is belt " belts}' grade.txt 
```

域值比较操作
```
$ awk '{if($6<27) print $0}' grade.txt
# 用引号将数字引用起来是可选的， "27" 、27产生同样的结果
# 给数字赋以变量名n和在BEGIN部分给变量赋值，两者意义相同
$ awk  'BEGIN {n="27" } {if($6 < n) print $0}' grade.txt
```
当在awk中修改任何域时，重要的一点是要记住实际输入文件是不可修改的，修改的只是保存在缓存里的awk复本。awk会在变量NR或NF变量中反映出修改痕迹。
如修改`J.Tsd`的目前级别分域，使其数值-1，使用赋值语句 $6 = $6 - 1 ，当然在实施修改前首先要匹配域名
```
$ awk '{if($1=="J.Tsd") $6=$6-1;print $1,$6,$7}' grade.txt 
J.Tsd 23 26  # 实际24
...
```

修改文本域将J.Tsd修改为J.test
```
$ awk '{ if($1=="J.Tsd") ($1="J.test"); print $1}' grade.txt 
J.test
...
```

只显示修改记录。上述例子均是对一个小文件的域进行修改，因此打印出所有记录查看修改部分不成问题，但如果文件很大，记录甚至超过100，打印所有记录只为查看修改部分显然不合情理。在模式后面使用花括号将只打印修改部分。
取得模式，再根据模式结果实施操作，可能有些抽象，现举一例，只打印修改部分。注意花括号的位置
```
$ awk '{ if($1=="J.Tsd") {$1="J.test" ;print $1}}' grade.txt
```

创建新的输出域

在awk中处理数据时，基于各域进行计算时创建新域是一种好习惯。创建新域要通过其他域赋予新域标识符。如创建一个基于其他域的加法新域{ $4 = $2 + $3 }
```
$ awk 'BEGIN{print "name\t Difference"} {if($6<$7) {$8=$7-$6; print $1,$8}}' grade.txt
$ awk 'BEGIN{print "name\t Difference"} {if($6<$7){diff=$7-$6;print $1,diff} }' grade.txt
```

增加列值

为增加列数或进行运行结果统计，使用符号 `+=`。增加的结果赋给符号左边变量值，增加到变量的域在符号右边。例如将 $1加入变量total，表达式为total += $1。
列值增加很有用。许多文件都要求统计总数，但输出其统计结果十分繁琐。在awk中这很简单，请看下面的例子。将所有学生的‘目前级别分’加在一起，方法是 tot += $6，tot即为awk浏览的整个文件的域6结果总和。所有记录读完后，
在 END部分加入一些提示信息及域6总和。不必在awk中显示说明打印所有记录，每一个操作匹配时，这是缺省动作

```
$ awk '(tot+=$6);END{print "Club student total points :" tot}' grade.txt 
J.Tsd 06/99 48421 Green 9 24 26
P.Bad 02/99  48   yellow 12 35 28
J.Tsad 07/99 4842  Brown-3 12 26 26
L.Tsad 05/99 4712  Brown-2 12 30 28:
Club student total points :115
```
如果文件很大，你只想打印结果部分而不是所有记录，在语句的外面加上{}即可
```
$ awk '{(tot+=$6)};END{print "Club student total points :" tot}' grade.txt 
Club student total points :115
```
统计当前目录下文件的长度
```
# 下面的正则表达式表明必须匹配行首，并排除字符d，表达式为^[^d]
$ ls -l |awk '/^[^d]/ {(tot+=$5); print $9,$5} END {print "total: "tot}'
```


精确匹配
```
$ awk '{if($3~/48/) print $0}' test.txt 
J.Tsd 06/99 48421 Green 9 24 26
P.Bad 02/99  48   yellow 12 35 28
J.Tsad 07/99 4842  Brown-3 12 26 26
```
上边的awk将返回所有序号带48的记录。为精确匹配48，使用等号`==`，并用双引号括起条件。例如 $3 ==“48” ，这样确保只有 48序号得以匹配，其余则不行
```
$ awk '{if($3=="48") print $0}' grade.txt  
P.Bad 02/99  48   yellow 12 35 28

```

为抽取级别为yellow或brown的记录，使用竖线符|(或关系匹配)。注意，使用竖线符时，语句必须用圆括号括起来

```
$ awk '$0~/(yellow|Brown)/' grade.txt 
```

复合模式或复合操作符用于形成复杂的逻辑操作，复杂程度取决于编程者本人。有必要了解的是，复合表达式即为模式间通过使用下述各表达式互相结合起来的表达式：

 - `&& AND`     语句两边必须同时匹配为真。
 - `||  O R`    语句两边同时或其中一边匹配为真。
 - `!`          非(求逆)

```
$ awk '{if($1=="P.Bad" && $4=="yellow") print $0}' grade.txt 
$ awk '{if($4~/Brown/ || $4=="yellow") print $0}' grade.txt 
```

**内置变量**

 - ARGC  命令行参数个数
 - ARGV  命令行参数排列
 - ENVIRON  支持队列中系统环境变量的使用
 - FILENAME  awk浏览的文件名
 - FNR    浏览文件的记录数
 - FS    设置输入域分隔符，等价于命令行—F 选项
 - NF    浏览记录的域个数
 - NR    已读的记录数
 - OFS    输出域分隔符
 - ORS    输出记录分隔符
 - RS     控制记录分隔符
 
```
$ awk '{print NF, NR, $0} END {print FILENAME}' grade.txt 

# NF的一个强大功能是将变量 $PWD的返回值传入awk并显示其目录。这里需要指定域分隔符/
$ echo $PWD |awk -F/ '{print $NF}'
```

**内置字符串函数**
 
  - gsub(r,s)   在整个$0中用s替换r
  - gsub(s,s,t)  在整个t中用s替换r
  - index(s,t)   返回s中字符串t的第一个位置
  - length(s)    函数返回字符串s字符长度
  - match(s,r)   测试s是否包含匹配r的字符窜
  - split(s,a,fs) 在fs上将s分成序列a
  - sprint(fmt, exp)  返回经fmt格式化后的exp (似于printf函数)
  - sub(r,s)    用$0中最左边最长的子串代替s
  - substr(s,p)  返回字符串s中从p开始的后缀部分
  - substr(s,p,n) 返回字符串s中从p开始长度为n的后缀部分

grub函数有点类似于sed查找和替换。它允许替换一个字符串或字符为另一个字符串或字符，并以正则表达式的形式执行。第一个函数作用于记录 $0，第二个gsub函数允许指定目标，然而，如果未指定目标，缺省为$0。

`gsub`要在整个记录中替换一个字符串为另一个，使用正则表达式格式， (/目标模式/，替换模式)。例如改变学生序号4842到4899
```
$ awk '{if($3=="4842") {gsub(/4842/,4899) ;print $0}}' grade.txt 
J.Tsad 07/99 4899  Brown-3 12 26 26
$ awk '$3=="4842" {gsub(/4842/,4899) ;print $0}' grade.txt
# 所有匹配替换
$ awk 'gsub(/4842/,4899){print $0}' grade.txt
```

`index`查询字符串s中t出现的第一位置。必须用双引号将字符串括起来。例如返回目标字符串Bunny中ny出现的第一位置
```
$ awk 'BEGIN{print index("Bunny","ny")}' 
4
``` 

`length`返回所需字符串长度，例如检验字符串 P.Bad返回名字及其长度，即人名构成的字符个数
```
$ awk '$1=="P.Bad" {print length($1)" " $1}' grade.txt
5 P.Bad
# 测试字符串长度
$ awk 'BEGIN {print length("I am wsm")}'
8
```

`match`测试目标字符串是否包含查找字符的一部分。可以对查找部分使用正则表达式，返回值为成功出现的字符排列数。如果未找到，返回0，
第一个例子在ANCD中查找d。因其不存在，所以返回0。第二个例子在ANCD中查找C。因其存在，所以返回ANCD中D出现的首位置字符数。第三个例子在学生J.Tsad中查找a
```
$ awk 'BEGIN {print match("ABCD",/d/)}'
0
$ awk 'BEGIN {print match("ABCD",/C/)}'
3
$ awk '$1=="J.Tsad" {print match($1,"a")}' grade.txt 
5
```

`split` 返回字符串数组元素个数。工作方式如下：如果有一字符串，包含一指定分隔符- ，例如AD2-KP9-JU2-LP-1，将之划分成一个数组。使用split指定分隔符及数组名。此例中，
命令格式为("AD2-KP9-JU2-LP-1"，parts_array，"-"） ，split然后返回数组下标数，这里结果为4。
```
$ awk 'BEGIN {print split("123#wsm#345",arr,"#")}'
3
# 这个例子中，split返回数组arr 的下标数。数组arr取值如下：
Arr[1]=”123”
Arr[2]=”wsm”
Arr[3]=”345
```

 `sub`发现并替换模式的第一次出现位置。字符串STR包含"poped popo pill" ，执行下列sub命令sub（/op/，"O P"，STR） 。模式op第一次出现时，进行替换操作，返回结果如下：‘pO Ped pope pill’ 。”
```
# 29 替换26
$ awk '$1=="J.Tsad" {sub(/26/,"29",$0); { print $0}}' grade.txt   # 只打印匹配模式
$  awk '$1=="J.Tsad" sub(/26/,"29",$0);{ print $0 }' grade.txt

```

`substr`是一个很有用的函数。它按照起始位置及长度返回字符串的一部分
```
$ awk '$1=="L.Tsad" {print substr($1,1,5)}' grade.txt 
L.Tsa
# 如果给定长度值远大于字符串长度， awk将从起始位置返回所有字符
$ awk '$1=="L.Tsad" {print substr($1,1,99)}' grade.txt
```
`substr`的另一种形式是返回字符串后缀或指定位置后面字符。这里需要给出指定字符串及
其返回字串的起始位置。例如，从文本文件中抽取姓氏，需操作域1，并从第三个字符开始
```
$ awk '{print substr($1,3)}' grade.txt
Tsd
Bad
Tsad
Tsad
```

#### printf
 - %c  ASCII 字符
 - %d  整数
 - %e  浮点数，科学计数法
 - %f  浮点数
 - %o  八进制数
 - %s  字符串
 - %x  十六进制数

字符转化 ASCII码中65的等价值。管道输出65到awk。printf进行ASCII码字符转换。这里也加入换行，因为缺省情况下printf不做换行动作
```
$ echo "65" |awk '{printf "%c\n",$0}'
A
$  awk 'BEGIN {printf "%c\n",65}'
A
$ awk 'BEGIN {printf "%f\n",999}'
999.000000
# 打印所有的学生名字和序列号，要求名字左对齐， 15个字符长度，后跟序列号
$ awk '{printf "%-15s %s\n",$1,$3}' grade.txt 
J.Tsd           48421
P.Bad           48
J.Tsad          4842
L.Tsad          4712
```

要快速查看文件系统空间容量，观察其是否达到一定水平，可使用下面awk一行脚本。因为要监视的已使用空间容量不断在变化，可以在命令行指定一个触发值。首先用管道命令将
df -k传入awk，然后抽出第4列，即剩余可利用空间容量。使用 $4~/^[0-9]/取得容量数值（1024块）而不是df的文件头，然后对命令行与`'if($4<TRIGGER)'`上变量TRIGGER中指定的值进行查询测试。
```
$ df -k |awk '($4~/^[0-9]/) {if($4<TRIGGER) print $6"\t"$4}' TRIGGER=300000
/run/lock   5116
/boot/efi   275404
```



在BEGIN部分定义字符串，在END部分返回从第t个字符开始抽取的子串。
```
$ awk 'BEGIN{str="I AM a GOOD BOY"} END {print substr(str,8)}' grade.txt 
GOOD BOY
```
循环数组
```
$ awk 'BEGIN {split("123#wsm#345",arr,"#")} END {for(i in arr) {print arr[i]}}' /dev/null 
345
wsm
123
```


通过BEGIN和END打印报头和报尾

```
awk -F ':' 'BEGIN{print "name   Belt\n-----"} {print $1"\t"$4} END {print "end-of report"}' aaa.txt

name   Belt
-----
root    0
...
end-of report

```

通过管道结合tee命令，在输出到文件的同时输出到屏幕（在测试输出结果正确与否时多使用这种方法）
```
awk '{print $0}' /etc/hosts  |tee  hosts.back
```


