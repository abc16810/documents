#### web墨卡托投影介绍

墨卡托投影，是正轴等角圆柱投影。由荷兰地图学家墨卡托(G.Mercator)于1569年创立。

这种投影方案的主要特点是，不再把地球当做椭球，而当做半径为6378137米的标准球体，以此来简化计算。动画演示[点击打开链接](http://cdn.hujiulong.com/geohey/blog/mercator/play.html)  可以很直观的看懂原理。



#### 计算

根据2πR赤道周长算出投影坐标 x[-20037508.3427892,20037508.3427892]，y轴范围与x轴范围一样长的规则定出投影坐标y[-20037508.3427892,20037508.3427892]

根据web墨卡托投影公式算出维度 `math.atan(math.sinh(math.pi))*180/math.pi` =  85.05112877980659

所以web墨卡托的经纬度投影范围：经度[-180,180]，维度[-85.05112877980659,85.05112877980659];

#### 瓦片

瓦片尺寸为256即为(256*256)。

0级瓦片的分辨率 = 2 * π * 6378137 / 256  =   156543.03390625  瓦片个数1

N级瓦片的分辨率 = 0级瓦片的分辨率/2n  瓦片个数`pow(2,n)* pow(2,n)`

![1647334696155](C:\Users\wsm\AppData\Roaming\Typora\typora-user-images\1647334696155.png)

| Resolution (per pixel) | Tile Matrix Set (WMTS)       | Zoom Levels | Max Resolution (deg/pixel) | Min Resolution (deg/pixel) |
| ---------------------- | ---------------------------- | ----------- | -------------------------- | -------------------------- |
| 19.10925707129405m     | GoogleMapsCompatible_Level13 | 13          | 156543.03390625            | 19.10925707129405          |
| 38.21851414258810m     | GoogleMapsCompatible_Level12 | 12          | 156543.03390625            | 38.21851414258810          |
| 305.7481131407048m     | GoogleMapsCompatible_Level9  | 9           | 156543.03390625            | 305.7481131407048          |
| 611.4962262814100m     | GoogleMapsCompatible_Level8  | 8           | 156543.03390625            | 611.4962262814100          |
| 1222.992452562820m     | GoogleMapsCompatible_Level7  | 7           | 156543.03390625            | 1222.992452562820          |
| 2445.984905125640m     | GoogleMapsCompatible_Level6  | 6           | 156543.03390625            | 2445.984905125640          |
| 4891.969810251280m     | GoogleMapsCompatible_Level5  | 5           | 156543.03390625            | 4891.969810251280          |
|                        |                              | 4           |                            | 9783.939620502560          |
|                        |                              | 3           |                            | 19567.879241005120         |
|                        |                              | 2           |                            | 39135.758482010240         |
|                        |                              | 1           |                            | 78271.516964020480         |
|                        |                              | 0           |                            |                            |

最大缩放级别为24



**morecantile**（墨卡托坐标和瓦片实用程序）

```
WEB_MERCATOR_TMS = morecantile.tms.get("WebMercatorQuad")
>>> WEB_MERCATOR_TMS.rasterio_crs
CRS.from_epsg(3857)
>>> WEB_MERCATOR_TMS.zoom_for_res(90274.46)  # 计算缩放级别 瓦片大小为256*256
1

def get_maximum_overview_level(width, height, minsize=256):
    overview_level = 0
    overview_factor = 1
    while min(width // overview_factor, height // overview_factor) > minsize:
        overview_factor *= 2
        overview_level += 1

    return overview_level
# minzoom是由最大理论overview level的分辨率定义的
overview_level = get_maximum_overview_level(w, h, minsize=256)
ovr_resolution = resolution * (2 ** overview_level)
minzoom = self.tms.zoom_for_res(ovr_resolution)

# 在TMS坐标参考系统中返回贴图的边界。
>>> WEB_MERCATOR_TMS.xy_bounds(0,0,0)
BoundingBox(left=-20037508.342789244, bottom=-20037508.342789244, right=20037508.342789244, top=20037508.342789244)


>>> mercantile.tile(0,1,2)  # 通过lng lat(左上) 及缩放级别 得到墨卡托 瓦片索引
Tile(x=2, y=1, z=2)
>>> mercantile.xy_bounds(2,1, 2)  # 通过瓦片索引得到瓦片边界
Bbox(left=0.0, bottom=0.0, right=10018754.171394622, top=10018754.171394622)

>>> d = mercantile.Tile(x=2, y=1, z=2)
>>> mercantile.bounds(d)  # 通过瓦片获取lnglat边界
LngLatBbox(west=0.0, south=0.0, east=90.0, north=66.51326044311186)

>>> mercantile.ul(1,1,2) #返回瓦片左上方的经度和纬度
LngLat(lng=-90.0, lat=66.51326044311186)
# 转换经度和纬度到网络墨卡托x, y
>>> mercantile.xy(*mercantile.ul(1,1,2))
(-10018754.171394622, 10018754.171394626)
# 得到一个平铺的quadkey
>>> mercantile.quadkey(0,0,2)
'00'
>>> mercantile.quadkey(0,0,3)
'000'
>>> mercantile.quadkey_to_tile('33')
Tile(x=3, y=3, z=2)
# 父瓦片
>>> mercantile.parent(3,3,2)
Tile(x=1, y=1, z=1)

>>> mercantile.children(mercantile.parent(3, 3, 2))
[Tile(x=2, y=2, z=2), Tile(x=3, y=2, z=2), Tile(x=3, y=3, z=2), Tile(x=2, y=3, z=2)]
```



tif 格式EPSG4326 -> EPSG3857  (32768 32768)  mrf格式

图像重投影和变形 创建vrt

```
gdalwarp -q -overwrite -of vrt -s_srs EPSG:4326 -t_srs EPSG:3857 input.tif output_reproject.vrt
```

计算栅格大小（分辨率）

```
target_extents = '-20037508.34,-20037508.34,20037508.34,20037508.34'  # 3857的边界
target_xmin, target_ymin, target_xmax, target_ymax = target_extents.split(',')
xres = repr(abs((float(target_xmax)-float(target_xmin))/float(target_x)))
yres = repr(abs((float(target_ymin)-float(target_ymax))/float(target_y)))
```

从数据集列表构建VRT

```
gdalbuildvrt -q -input_file_list  output_files  -te -20037508.34 -20037508.34 20037508.34 20037508.34 -a_srs EPSG:3857 -resolution user -tr 1222.9924523925781 1222.9924523925781 -vrtnodata 0 -srcnodata 0  target.vrt 
# -te 设置VRT文件的地理参考区。这些值必须以地理引用的单位表示。如果没有指定，VRT的范围是源光栅集的最小边界框
# -resolution user  指定计算输出分辨率的方式user 必须与-tr选项结合使用来指定目标分辨率。
# -tr  设定目标分辨率
# -a_srs 覆盖输出文件的投影
# -vrtnodata 设置nodata值(每个频段可以提供不同的值)
# -srcnodata 为输入频段设置nodata值(可以为每个频段提供不同的值)
```

不同格式之间转换光栅数据

```
gdal_translate -q -of MRF -co COMPRESS=JPEG -co BLOCKSIZE=256 -outsize 32768 32768 -co QUALITY=80 -co NOCOPY=true -co UNIFORM_SCALE=2 target.vrt target.MRF
```

 获取vrt的边界，如果vrt的边界超出范围，再次用gdalwarp调整

```
gdalinfo -json output_reproject.vrt
ulx = ["cornerCoordinates"]["upperLeft"][0]
uly = ["cornerCoordinates"]["upperLeft"][1]
lrx = ["cornerCoordinates"]["lowerRight"][0]
lry = ["cornerCoordinates"]["lowerRight"][1]

gdalwarp -overwrite -of VRT -te -20037506.531 -20037508.34 20037390.272 20037508.34 output_reproject.vrt output_reproject.vrt._cut.vrt
# -te 设置要创建的输出文件的地理引用
```

通过block size 计算最大缩放级别的瓦片个数

```
x_size = y_size = 32768
block_x = 256
block_y = 256
while (block_x*2) < x_size:
block_x = block_x * 2
while (block_y*2) < y_size:
block_y = block_y * 2
```



gdalwarp -overwrite -of VRT -te -20037506.531 -20037508.34 20037390.272 20037508.34

gdalwarp -q -overwrite -of GTiff -s_srs EPSG:4326 -t_srs EPSG:3857 log_k_s_l6.tif  log_k_s_l6_3857_2.tif

```
gdalwarp -q -overwrite -of GTiff -s_srs EPSG:4326 -t_srs EPSG:3857 -te -20037508.34 -20037508.34 20037508.34 20037508.34 -tr 1222.9924523925781 1222.9924523925781 -co COMPRESS=DEFLATE -co TILED=YES  log_k_s_l6.tif  log_k_s_l6_3857.tif
```

```
gdalwarp -q -overwrite -of vrt -s_srs EPSG:4326 -t_srs EPSG:3857  SA.vrt SA_3857_2.tif
# 不指定te 边界，默认是in target SRS by default 有超出边界的可能
```

rasterio

```
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

dst_crs = 'EPSG:4326'

with rasterio.open('rasterio/tests/data/RGB.byte.tif') as src:
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height
    })

    with rasterio.open('/tmp/RGB.byte.wgs84.tif', 'w', **kwargs) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest)
```





https://docs.opengeospatial.org/is/17-083r2/17-083r2.html



