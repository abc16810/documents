##### pandas读取CSV文件

使用函数：pandas.read_csv()

- filepath_or_buffer：路径，也可以是URL、文件对象

```
import pandas as pd
pd.read_csv("xxx.csv")
pd.read_csv("http://localhost/xxx.csv")
f = open("xxx.csv", encoding="utf-8")
pd.read_csv(f)
```

- sep：指定分隔符。如果不指定参数，默认使用逗号分隔，多空格可使用'\s+' 

```
pd.read_csv("result.dat", sep='\s+')
```

- delimiter：  sep的别名，与 sep 功能相似 默认None

- header：指定行数用来作为列名，数据开始行数。默认infer。
  - 当names没被赋值时，header会变成0，即选取数据文件的第一行作为列名
  - 当 names 被赋值，header 没被赋值时，那么header会变成None。如果都赋值，就会实现两个参数的组合功能

```
>>> print(pd.read_csv("result.dat", sep='\s+'))  # header=0, names=None
                x            y         z        zb      u      v
0      591374.935  4286150.959  1163.470  1163.366 -0.408 -0.195
1      591376.935  4286150.959  1163.476  1163.270 -0.282 -0.181
2      591362.935  4286152.959  1163.410  1163.270 -0.480 -0.027
...
>>> print(pd.read_csv("result.dat", sep='\s+', names=[1,2,3,4,5,6]))  # header=None 
                1            2         3         4       5       6
0               x            y         z        zb       u       v
1      591374.935  4286150.959  1163.470  1163.366  -0.408  -0.195
2      591376.935  4286150.959  1163.476  1163.270  -0.282  -0.181
>>> print(pd.read_csv("result.dat", sep='\s+', names=[1,2,3,4,5,6], header=0))
                1            2         3         4      5      6
0      591374.935  4286150.959  1163.470  1163.366 -0.408 -0.195
1      591376.935  4286150.959  1163.476  1163.270 -0.282 -0.181
2      591362.935  4286152.959  1163.410  1163.270 -0.480 -0.027
# 这个相当于先不看names，只看header，我们说header等于0代表是把第一行当做表头，下面的当成数据，然后再把表头用names给替换掉
>>> print(pd.read_csv("result.dat", sep='\s+', names=[1,2,3,4,5,6], header=3))
                1            2         3         4      5      6
0      591364.935  4286152.959  1163.398  1163.265 -0.598 -0.116
1      591366.935  4286152.959  1163.405  1163.213 -0.677 -0.067
2      591368.935  4286152.959  1163.410  1163.213 -0.704 -0.096
# header=3，表示第四行当做表头，第四行下面当成数据,然后再把表头用names给替换掉
```

**names和header的使用场景主要**

1. csv文件有表头并且是第一行，那么names和header都无需指定
2. csv文件有表头、但表头不是第一行，可能从下面几行开始才是真正的表头和数据，这个时候指定header即可
3. csv文件没有表头，全部是纯数据，那么我们可以通过names手动生成表头
4. csv文件有表头、但是这个表头你不想用，这个时候同时指定names和header。先用header选出表头和数据，然后再用names将表头替换掉

- index_col  指定索引列 默认None(在读取文件之后，生成的 DataFrame 的索引默认是0 1 2 3)

```
>>> print(pd.read_csv("result.dat", sep='\s+', index_col='x')) # 指定x列为索引 或者指定1
                      y         z        zb      u      v
x                                                        
591374.935  4286150.959  1163.470  1163.366 -0.408 -0.195
591376.935  4286150.959  1163.476  1163.270 -0.282 -0.181
591362.935  4286152.959  1163.410  1163.270 -0.480 -0.027
```

- usecols: 返回一个数据子集，该列表中的值必须可以对应到文件中的位置（数字可以对应到指定的列）

```
# 如果列有很多，而我们不想要全部的列、而是只要指定的列就可以使用这个参数
# pd.read_csv("result.dat", sep='\s+', usecols=[0,1,2])
>>> print(pd.read_csv("result.dat", sep='\s+', usecols=['x','y','z']))
                x            y         z
0      591374.935  4286150.959  1163.470
1      591376.935  4286150.959  1163.476
2      591362.935  4286152.959  1163.410
# 此外 use_cols 还有可以接收一个函数，会依次将列名作为参数传递到函数中进行调用，如果返回值为真，则选择该列，不为真，则不选择
>>> pd.read_csv("result.dat", sep='\s+', usecols=lambda x: len(x) >=2 )
             zb
0      1163.366
1      1163.270
```

- mangle_dupe_cols: 默认True，数据会含有重名的列，重名的列导入后面多一个 .1。如果设置为 False，会抛出不支持的异常
- prefix:  当导入的数据没有 header 时，设置此参数会自动加一个前缀。我们看到在不指定names的时候，header默认为0，表示以第一行为表头。但如果不指定names、还显式地将header指定为None，那么会自动生成表头0 1 2 3...

```
>>> pd.read_csv('22.csv', delim_whitespace=True, header=None, prefix="T")
                        T0   T1   T2
0             1,2,3,4,5,6,   7,  8.0
1           a,b,c,d,e,f,g,    h  NaN
```

- delim_whitespace:  默认为 False，设置为 True 时，表示分割符为空白字符，可以是空格、"\t"等等

```
pd.read_csv('girl.csv',delim_whitespace=True) # pd.read_csv("result.dat", sep='\s+')
# 不管分隔符是什么，只要是空白字符，那么可以通过delim_whitespace=True进行读取
```

- converters: 读取的时候对列数据进行变换

```
>>> pd.read_csv("result.dat", sep='\s+', converters={"z": lambda x: float(x)/100})
                x            y         z        zb      u      v 
0      591374.935  4286150.959  11.63470  1163.366 -0.408 -0.195  
1      591376.935  4286150.959  11.63476  1163.270 -0.282 -0.181 
2      591362.935  4286152.959  11.63410  1163.270 -0.480 -0.027  
# 将z除以100，但是注意 float(x)，在使用converters参数时，解析器默认所有列的类型为 str，所以需要显式类型转换。
```

- engine: pandas解析数据时用的引擎，pandas 目前的解析引擎提供两种：c、python，默认为 c，因为 c 引擎解析速度更快，但是特性没有 python 引擎全。如果使用 c 引擎没有的特性时，会自动使用为 python 引擎。如果sep是单个字符，或者字符串\s+，那么C是可以解决的。但如果我们指定的sep比较复杂，这时候引擎就会退化
- dtype: 指定某个列的类型, 比如`0100012521` 字符串默认会解析成整型，结果把开头的0给丢了。这个时候我们就可以通过dtype来指定某个列的类型

```
pd.read_csv('xxx.csv', delim_whitespace=True, dtype={"id": str})
```

- true_values和false_value: 设定缺测值

```
# 指定哪些值应该被清洗为True，哪些值被清洗为False
>>> a = pd.read_csv("result.dat", sep='\s+', true_values=['tom', "kcc", "zzx"], false_values=['luc'])
                x            y         z        zb      u      v   name
0      591374.935  4286150.959  1163.470  1163.366 -0.408 -0.195   True
1      591376.935  4286150.959  1163.476  1163.270 -0.282 -0.181   True
2      591362.935  4286152.959  1163.410  1163.270 -0.480 -0.027  False
# 注 当某一列的数据全部出现在true_values + false_values里面，才会被替换
```

- skiprows: 设定需要跳过的行号(从前往后)

```
# 注: 这里是先过滤，然后再确定表头,第一行过滤掉了，但是第一行是表头，所以过滤掉之后，第二行就变成表头.
# 如果过滤掉第二行，那么只相当于少了一行数据，但是表头还是原来的第一行
>>> pd.read_csv("result.dat", sep='\s+', skiprows=[0])
       591374.935  4286150.959  1163.470  1163.366  -0.408  -0.195  
0      591376.935  4286150.959  1163.476  1163.270  -0.282  -0.181  
1      591362.935  4286152.959  1163.410  1163.270  -0.480  -0.027 
# 除了传入具体的数值，来表明要过滤掉哪些行，还可以传入一个函数
>>> pd.read_csv("result.dat", sep='\s+', skiprows=lambda x: x>0 and x % 2 == 0)
               x            y         z        zb      u      v 
0      591374.935  4286150.959  1163.470  1163.366 -0.408 -0.195  
1      591362.935  4286152.959  1163.410  1163.270 -0.480 -0.027  
2      591366.935  4286152.959  1163.405  1163.213 -0.677 -0.067 
```

- skipfooter : 设定需要跳过的行号(从后往前), 解析引擎退化为 Python。这是因为 C 解析引擎没有这个特性

```
pd.read_csv("result.dat", sep='\s+', skipfooter=3, engine="python")
# skipfooter接收整型，表示从结尾往上过滤掉指定数量的行，因为引擎退化为python，那么要手动指定engine="python"，不然会警告。另外需要指定encoding="utf-8"，因为csv存在编码问题，当引擎退化为python的时候，读取可能会乱码
```

- skipinitialspace: 是否忽略分隔符后的空格

```
>>> a = pd.read_csv("22.csv", sep=',')
>>> a.iloc[0][7] #' h'
>>> a = pd.read_csv("22.csv", sep=',', skipinitialspace=True)
>>> a.iloc[0][7] # 'h'
```

- nrows:  指定一次性读入的文件行数, 它在读入大文件时很有用

```
>>> pd.read_csv("result.dat", sep='\s+', nrows=2)  # 读取2条数据
            x            y         z        zb      u      v 
0  591374.935  4286150.959  1163.470  1163.366 -0.408 -0.195  
1  591376.935  4286150.959  1163.476  1163.270 -0.282 -0.181  
```

- na_values: 用于哪些值需要处理成 NaN

```
# 将tom和1163.470 替换为NaN
>>> pd.read_csv("result.dat", sep='\s+', na_values=['tom', '1163.470'])
                x            y         z        zb      u      v name
0      591374.935  4286150.959       NaN  1163.366 -0.408 -0.195  NaN
1      591376.935  4286150.959  1163.476  1163.270 -0.282 -0.181  NaN
# 通过字典实现只对指定的列进行替换
na_values={"z": ["1163.470"], "name": ["tom"]}
```

- keep_default_na: 将一些默认的值在读取的时候被替换成空值 如`1.#IND`,`N/A`  等等
- skip_blank_lines:  过滤掉空行, 默认True， 如为 False 则解析为 NaN

- na_filter:  是否进行空值检测，默认为 True，如果指定为 False, 那么 pandas 在读取 CSV 的时候不会进行任何空值的判断和检测，所有的值都会保留原样。因此，如果你能确保一个 CSV 肯定没有空值，则不妨指定 na_filter 为 False，因为避免了空值检测，可以提高大型文件的读取速度。另外，该参数会屏蔽 keep_default_na 和 na_values，也就是说，当 na_filter 为 False 的时候，这两个参数会失效

- parse_dates/date_parser： 解析日期类型，一般搭配下面的date_parser使用

```
pd.read_csv("result.dat", sep='\s+', parse_dates=['date'], date_parser=lambda x: datetime.strptime(x, "%Y年%m月%d日"))
```

- infer_datetime_format

infer_datetime_format 参数默认为 False。如果设定为 True 并且 parse_dates 可用，那么 pandas 将尝试转换为日期类型，如果可以转换，转换方法并解析，在某些情况下会快 5~10 倍

- verbose 打印额外信息

```
>>> pd.read_csv("result.dat", sep='\s+', verbose=True)
Tokenization took: 22.82 ms
Type conversion took: 8.41 ms
Parser memory cleanup took: 0.01 ms
```

- iterator:  iterator 为 bool类型，默认为False。如果为True，那么返回一个 TextFileReader 对象，以便逐块处理文件。这个在文件很大、内存无法容纳所有数据文件时，可以分批读入，依次处理

```
>>> a = pd.read_csv("result.dat", sep='\s+', iterator=True)
>>> a
<pandas.io.parsers.TextFileReader object at 0x7f7b1d5e01d0>
>>> a.get_chunk(100)  # 读取前100条数据
>>> a.get_chunk(10)   # 读取100 - 109条数据
```

- chunksize： 默认为 None，设置文件块的大小

```
a = pd.read_csv("result.dat", sep='\s+', chunksize=1000)  # 设置块大小为1000
# 调用get_chunk，如果不指定行数，那么就是默认的chunksize
>>> print(chunk.get_chunk())  # 前1000条数据
>>> a.get_chunk(100)  # 第1000-1099条数据
```

- compression: compression 参数取值为` {'infer', 'gzip', 'bz2', 'zip', 'xz', None}`，默认 `infer`

```
# 直接将上面的xxx.csv添加到压缩文件，打包成xxx.zip
pd.read_csv('xxx.zip', sep="\t", compression="zip")
```

- encoding:  指定字符集类型，通常指定为 'utf-8'。根据情况也可能是'ISO-8859-1'

- thousands:  千分位分割符，如 , 或者 .，默认为None





