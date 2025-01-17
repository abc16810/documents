#### 变量值互换
```
a, b = 1, 2; a, b = b, a
```

#### 解决FizzBuzz问题
FizzBuzz问题：打印数字1到100, 3的倍数打印“Fizz”, 5的倍数打印“Buzz”

```
for x in range(1, 101): print("fizz"[x % 3 * 4:]+"buzz"[x % 5 * 4:] or x) 

# 数组
[(not i%3)*"Fizz" + (not i%5)*"Buzz" or str(i) for i in range(1, 100+1)]
```
#### 输出特定字符
输出`Love`拼成的心形

```
print('\n'.join([ ' '.join([ ( 'Love'[(x-y) % len('Love') ] if ((x*0.05)**2+(y*0.1)**2-1)**3-(x*0.05)**2*(y*0.1)**3 <= 0 else ' ' )  for x in range(-30,30) ])  for y in range(30,-30, -1)]))
```

#### 九九乘法表

```
print ('\n'.join([ '\t'.join([ '%s*%s=%-2s' % (y,x, x*y) for y in range(1, x+1) ])   for x in range(1,10)]))
1*1=1 
1*2=2 	2*2=4 
1*3=3 	2*3=6 	3*3=9 
1*4=4 	2*4=8 	3*4=12	4*4=16
1*5=5 	2*5=10	3*5=15	4*5=20	5*5=25
1*6=6 	2*6=12	3*6=18	4*6=24	5*6=30	6*6=36
1*7=7 	2*7=14	3*7=21	4*7=28	5*7=35	6*7=42	7*7=49
1*8=8 	2*8=16	3*8=24	4*8=32	5*8=40	6*8=48	7*8=56	8*8=64
1*9=9 	2*9=18	3*9=27	4*9=36	5*9=45	6*9=54	7*9=63	8*9=72	9*9=81
```

#### 计算出1-100之间的素数
```
print(' '.join([str(item) for item in filter(lambda x: not [x % i for i in range(2, x) if x % i == 0], range(2, 101))]))
2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97
```

#### 斐波那契数列
```
print([x[0] for x in [ (a[i][0], a.append([a[i][1], a[i][0]+ a[i][1]])) for a in ([[1,1]],) for i in range(10) ]])
[1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

#### 八皇后问题
```
>>> [  __import__('sys').stdout.write("\n".join('.'*i + 'Q' + '.'*(4-i-1) for i in vec ) + "\n=========\n")  for vec in __import__( 'itertools' ).permutations(range(4)) if 4 == len(set( vec[i]+i for i in range(4) )) == len(set( vec[i]-i for i in range(4) ))]
.Q..
...Q
Q...
..Q.
=========
..Q.
Q...
...Q
.Q..
=========
[30, 30]

```
#### 平铺数组
实现数组的flatten功能: 将多维数组转化为一维
```
>>> flatten = lambda x: [y for l in x for y in flatten(l)] if isinstance(x, list) else [x]
>>> flatten([1,2,3,4,[5,6],7])
[1, 2, 3, 4, 5, 6, 7]

```

#### 实现list 大小切分
```
array = lambda x: [x[i:i+3] for i in range(0, len(x), 3)]
```

#### 杨辉三角

```
# 特点
[
[1]
[1,1]   =  0 1 + 1 0
[1,2,1]  =  0 1 1 + 1 1 0
[1,3,3,1] =  0 1 2 1 + 1 2 1 0
]

# python2
res = [[1]]
[ x[0] for x in [ (res[i], res.append(map(lambda x,y: x+y, [0]+res[-1], res[-1]+[0])))  for i in range(7) ]]
[[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1], [1, 5, 10, 10, 5, 1], [1, 6, 15, 20, 15, 6, 1]]
```
