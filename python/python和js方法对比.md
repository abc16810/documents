#### MD5加密
```
# JS的MD5加密实现(模块CryptoJS v3.1.2)
key = '123456789'
var a=CryptoJS.MD5(key)
a.toString()
"25f9e794323b453885f5181f1b624d0b"

# python的MD5加密实现
>>> import hashlib
>>> s = hashlib.md5()
>>> key = '123456789'
>>> s.update(key)
>>> res = s.hexdigest()
>>> print(res)
25f9e794323b453885f5181f1b624d0b
```


#### 字典对象排序

```
# js
var a= {'aa': '222', '11': '444', '3': 1, 'bb': '444', 'ccc': 'the is a test'}
var newObject = {};
Object.keys(a).sort().map(function(key) {
            //console.log(key);  
            newObject[key] = a[key]
        });
// newObject    
// {3: 1, 11: "444", aa: "222", bb: "444", ccc: "the is a test"}

# python

>>> import collections
>>> d1=collections.OrderedDict()
>>> a = {'aa': '222', '11': '444', '3': 1, 'bb': '444', 'ccc': 'the is a test'}
>>> for x in sorted(a):  # sorted(a) 和 Object.keys(a).sort() 结果相同
...  d1[x] = a[x]
>>> d1
OrderedDict([('11', '444'), ('3', 1), ('aa', '222'), ('bb', '444'), ('ccc', 'the is a test')])   # 这边显示的循序和 newObject 不同

# 如果和上述js的 newObject 结果相同 我们用key （如果是数字的话）的大小排序
>>> sorted(a.items(),key=lambda x:int(x[0]) if x[0].isdigit() else x[0]) 
[('3', 1), ('11', '444'), ('aa', '222'), ('bb', '444'), ('ccc', 'the is a test')]
```

#### 序列化

```
# js
var a = {'11': '444', '3': 1, 'aa': '222', 'bb': '444', 'ccc': 'the is a test'}
JSON.stringify(a)  # 对象a是排序后的object 
"{"3":1,"11":"444","aa":"222","bb":"444","ccc":"the is a test"}"

# python
>>> d1
OrderedDict([('3', 1), ('11', '444'), ('aa', '222'), ('bb', '444'), ('ccc', 'the is a test')])  # 有序字典(提前排好序)
>>> import json
>>> json.dumps(d1,separators=(',',':'), ensure_ascii=False)
'{"11": "444", "3": 1, "aa": "222", "bb": "444", "ccc": "the is a test"}'
```


#### base64
```
# js
var mybase64 = new Base64();
var a = {'11': '444', '3': 1, 'aa': '222', 'bb': '444', 'ccc': 'the is a test'}
mybase64.encode(JSON.stringify(a))
"eyIzIjoxLCIxMSI6IjQ0NCIsImFhIjoiMjIyIiwiYmIiOiI0NDQiLCJjY2MiOiJ0aGUgaXMgYSB0ZXN0In0="

# python
>>> json.dumps(d2, separators=(',',':')) # d2提前排好序
'{"3":1,"11":"444","aa":"222","bb":"444","ccc":"the is a test"}'
>>> res = json.dumps(d2, separators=(',',':'))
>>> base64.b64encode(res.encode())
b'eyIzIjoxLCIxMSI6IjQ0NCIsImFhIjoiMjIyIiwiYmIiOiI0NDQiLCJjY2MiOiJ0aGUgaXMgYSB0ZXN0In0='
```

#### DES加密

```
# js
var key = 'f2273fbf507ff357';
var iv = 'c50d6722';
var text  = mybase64.encode('123456789test')  //待加密的字符串 "MTIzNDU2Nzg5dGVzdA==" 
secretkey = CryptoJS.enc.Utf8.parse(key);
secretiv = CryptoJS.enc.Utf8.parse(iv);
var result = CryptoJS.DES.encrypt(text, secretkey, {
                iv: secretiv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            });
console.log(result.toString())
// uWD/KlEmZMH92PMCNkrFt+GDM5KZWTHr

# python
from Crypto.Cipher import DES
key = 'f2273fbf507ff357'
iv = 'c50d6722'
text  = base64.b64encode('123456789test')
BS = DES.block_size
mystr = text + (BS - len(text) % BS) * chr(BS - len(text) % BS).encode("utf-8")  # 定义 padding 即 填充 为PKCS7
key = key[:8] # 确保key 和iv 都是8位
iv = iv[:8]
cipher = DES.new(key, DES.MODE_CBC, iv)  # 加密模式为CBC
ret = base64.b64encode(cipher.encrypt(mystr))
print(ret)
# uWD/KlEmZMH92PMCNkrFt+GDM5KZWTHr
```

#### DES 解密

```
# js
var key = 'f2273fbf507ff357';
var iv = 'c50d6722';
secretkey = CryptoJS.enc.Utf8.parse(key);
secretiv = CryptoJS.enc.Utf8.parse(iv);
var text = 'uWD/KlEmZMH92PMCNkrFt+GDM5KZWTHr'; //上述加密后的字符串
var result = CryptoJS.DES.decrypt(text, secretkey, {
                iv: secretiv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            });
console.log(result.toString(CryptoJS.enc.Utf8))
// MTIzNDU2Nzg5dGVzdA==

# python
import pyDes
data = 'uWD/KlEmZMH92PMCNkrFt+GDM5KZWTHr' # 上述的加密字符串
key = 'f2273fbf507ff357'
iv = 'c50d6722'
key = key[:8]
encryptedData = base64.b64decode(data)   # base64 解码
des = pyDes.des(key, pyDes.CBC, iv, pad=None, padmode=pyDes.PAD_PKCS5)  
res = des.decrypt(encryptedData) # 解密
print(res.decode('utf-8'))
# MTIzNDU2Nzg5dGVzdA==

```
