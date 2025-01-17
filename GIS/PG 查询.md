相关简单查询

```
>>> from django.contrib.gis.geos import Polygon
>>> p = Polygon(((100, 30), (120, 30), (120, 40), (100, 40), (100, 30)))
>>> p.wkb.hex()   # 没有指定srid 16进制
'0103000000010000000500000000000000000059400000000000003e400000000000005e400000000000003e400000000000005e4000000000000044400000000000005940000000000000444000000000000059400000000000003e40'
# 查询所有模型字段的mpoly与改多边形相交的区域
select count(*) from test d where ST_Intersects(
ST_GeomFromEWKB('\x0103000000010000000500000000000000000059400000000000003e400000000000005e400000000000003e400000000000005e4000000000000044400000000000005940000000000000444000000000000059400000000000003e40') ,st_geomfromtext(ST_AsText(d.mpoly)))

>>> p.wkt
'POLYGON ((100 30, 120 30, 120 40, 100 40, 100 30))'
# ST_GeomFromText(p.wkt)
# ST_GeomFromText('SRID=4326;POINT (100 23)')

>>> from django.contrib.gis.geos import GEOSGeometry
>>> srid_p = GEOSGeometry(p, srid=4326)
>>> print(srid_p)
SRID=4326;POLYGON ((100 30, 120 30, 120 40, 100 40, 100 30))
>>> srid_p.ewkb.hex()  # 指定srid为4326
'0103000020e6100000010000000500000000000000000059400000000000003e400000000000005e400000000000003e400000000000005e4000000000000044400000000000005940000000000000444000000000000059400000000000003e40'
# st_geomfromtext(ST_AsText(d.geom), 4326) 指定srid
select count(*) from test d where ST_Intersects(
ST_GeomFromEWKB('\x0103000020e6100000010000000500000000000000000059400000000000003e400000000000005e400000000000003e400000000000005e4000000000000044400000000000005940000000000000444000000000000059400000000000003e40') ,st_geomfromtext(ST_AsText(d.geom), 4326))
# 或者 st_setsrid(ST_AsText(d.geom), 4326)) / st_setsrid(d.geom, 4326)
```

包含

```
SELECT ST_Contains(ST_MakePolygon(ST_GeomFromText('LINESTRING ( 121.312350 30.971457 , 121.156783 31.092221 , 121.353250 31.278195 , 121.509125 31.157431 , 121.312350 30.971457 )')) ,st_point(121.332378,31.07106));
 st_contains 
-------------
 t    # 返回t表示在范围内
(1 row)

# st_point(a,b) 表示为一个点

SELECT ST_Contains(ST_MakePolygon(ST_GeomFromText('LINESTRING (121.312350 30.971457 , 121.156783 31.092221, 121.353250 31.278195, 121.509125 31.157431, 121.312350 30.971457)')) ,st_point(121.632378,31.07106));
 st_contains 
-------------
 f   # 返回f表示不在范围内
(1 row)
```

**ST_Intersects(poly, geom)**   相交查询

![1647919396921](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647919396921.png)



**ST_Disjoint(poly, geom)** 测试几何图形字段是否与查找几何图形在空间上不相交

![1647920831385](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647920831385.png)



**ST_Touches(poly, geom)**测试几何图形字段是否在空间上接触查找几何图形

![1647923373307](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647923373307.png)



**`ST_Crosses(poly, geom)`**测试几何图形字段是否在空间上跨越

![1647923621347](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647923621347.png)



**ST_Within(poly, geom)**测试几何图形字段是否在查找几何图形内。

```
from django.contrib.gis.geos import Polygon, Point
>>> Point(24,23).within(Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))))
True
```

与 `ST_Contains` 含义相反  `ST_Within(A,B)`如果几何图形A完全在几何图形B内部，则返回true

![1647924039708](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647924039708.png)



**ST_Contains(poly, geom)** 测试几何图形字段是否在空间上包含查找几何图形

```
>>> Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))).contains(Point(24,23))
True
>>> Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))).contains(Point(0,0))  # 边界上的点不包含
False
```

```
ST_Contains(A, B)
```

当且仅当B的点不在A的外部，且B的内部至少有一个点在A的内部时返回真值

![1647924266594](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647924266594.png)





**ST_Overlaps(poly, geom)**测试几何图形字段是否在空间上与查找几何图形重叠

**ST_CoveredBy**  何图形字段中是否没有点在查找几何图形之外

**ST_Covers**   如果查找几何图形中没有点在几何图形字段之外

```
>>> b = Polygon(((25.0, 25.0), (50.0, 50.0), (75.0, 25.0), (50.0, 0.0), (25.0, 25.0)))
>>> d = LineString((50,23),(50,24))
>>> b.covers(d)
True
```

**&<**   几何图形字段的边界框是否与查找几何图形的边界框重叠或位于其左侧 (`overlaps left`)

**&>**   几何图形字段的边界框是否与查找几何图形的边界框重叠或位于其右侧(`overlaps right`)

**|&>* **  几何图形字段的边界框是否与查找几何图形的边界框重叠或位于其上方(`overlaps above`)

**&<|**  几何图形字段的边界框是否与查找几何图形的边界框重叠或低于查找几何图形的边界框(`overlaps below`)	

**`@`** 几何图形字段的边界框是否完全包含在查找几何图形的边界框中

```
A @ B
如果A的边界框被B的包围，则返回TRUE
```

**~**几何图形或光栅字段的边界框是否完全包含查找几何图形的边界框

```
A ~ B
如果A的边界框包含B，则返回TRUE   (与 @ 含义相反)
```

**&&**测试几何图形字段的边界框是否与查找几何图形的边界框重叠



```
>>> a = Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0)))
>>> b = Polygon(((25.0, 25.0), (50.0, 50.0), (75.0, 25.0), (50.0, 0.0), (25.0, 25.0)))
>>> a.overlaps(b)
True
>>> b.overlaps(a)
True
```

![1647924570575](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647924570575.png)

![1647931692921](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647931692921.png)



**ST_IsValid(poly)**  测试几何图形是否有效

**ST_Equals**几何图形字段在空间上等于查找几何图形

**ST_ContainsProperly** 如果查找几何图形与几何图形字段的内部相交，而不是与边界(或外部)相交，则返回true

**~=**  在PostGIS上，它测试边界的相等性

**<<**    几何图形字段的边界框是否严格地位于查找几何图形的边界框的左侧

```
select id, name from apps_worldborder where "mpoly" <<  ST_GeomFromText('SRID=4326;POLYGON ((140 50, 150 50, 140 60, 140 50))');
```

**>>**  几何图形字段的边界框是否严格地位于查找几何图形的边界框的右侧

**|>>** 几何图形字段的边界框是否严格高于查找几何图形的边界框(`strictly above`)

**<<|** 几何图形字段的边界框是否严格低于查找几何图形的边界框(`strictly below`)

**ST_DistanceSphere**	距离值 [参考](https://postgis.net/docs/ST_DistanceSphere.html)



#### 聚合函数

**ST_Union**  返回一个由查询集中每个几何图形的并集组成的GEOSGeometry对象。请注意，Union的使用是处理器密集型的，可能会在大型查询集上花费大量的时间

**ST_Collect** 从几何列返回一个几何集合或一个MULTI几何对象。这类似于Union聚合的简化版本，除了它可以比执行Union快几个数量级，因为它将几何图形卷成一个集合或多个对象，而不关心溶解边界

**ST_Extent**   返回范围为一个四元组，包括左下坐标和右上坐标

**ST_MakeLine**   返回由QuerySet中的点字段几何图形构造的LineString

